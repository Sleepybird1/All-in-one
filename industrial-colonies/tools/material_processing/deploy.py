"""Plan, then explicitly apply, the audited 0.5 material/Lithosphere batch.

Default mode is read-only. No Minecraft/KJSGen/build is launched. An accepted
runtime receipt and the exact dry-run plan digest are mandatory for --apply.
See DEPLOYMENT.md. This deliberately does not reuse the broad 0.4 deployer.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LIVE = Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
DEFAULT_STAGE = ROOT / 'isolated-runtime/geology-gametest-20260909-064550-754'
OLD_JAR = 'industrial_colonies-0.4.0.jar'
OLD_JAR_HASH = 'c053f1da65db73d8bd4158f8c082d51653efdbc6320de4d022e219fb0627f3b4'
NEW_JAR = 'industrial_colonies-0.5.0.jar'
OLD_PROJECT_HASH = 'f2ac4d50a62da9926dc02da67c3c34d9b77032d3b1c4d11b9ea3d8ea4596a79c'
PROJECT = 'kjsgen/projects/default.json'
EXPORT = 'kubejs/server_scripts/kjsgen_recipes.js'
SCRIPT = 'kubejs/server_scripts/zz_industrial_material_processing.js'
RETIRED_CARD = 'industrial_colonies:nuclear/refined_radiance'
SELECTED = {'industrial_colonies:' + key for key in (
    'manufacturing/industrial_iron/deployer', 'manufacturing/industrial_iron/mixer',
    'manufacturing/industrial_iron/press', 'manufacturing/industrial_iron/saw',
    'manufacturing/industrial_iron/fan', 'manufacturing/industrial_iron/roller',
    'mekanism/thermal_evaporation/block_batch', 'mekanism/thermal_evaporation/controller',
    'mekanism/thermal_evaporation/valve', 'mekanism_components/basic_chemical_tank',
    'mekanism_components/electrolytic_core', 'mekanism_pre_nuclear/electrolytic_separator',
    'mekanism_pre_nuclear/chemical_infuser', 'mekanism_pre_nuclear/chemical_oxidizer',
    'fluid_infrastructure/fireproof_chemical_vat', 'heavy_industry/industrial_mixer',
    'tfmg_heavy_electrical/electrode_holder', 'material_bootstrap/metallurgic_infuser',
    'material_bootstrap/rotary_condensentrator')}
ALLOWED_REMOVALS = {'mekanism:metallurgic_infuser', 'mekanism:rotary_condensentrator',
                    'tfmg:crafting/materials/industrial_mixer',
                    'createcasing:crafting/roller/industrial_iron'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe(path):
    """Reject links/junctions at every existing path component, before resolve."""
    path = Path(os.path.abspath(path))
    for component in (path, *path.parents):
        if component.exists() or component.is_symlink():
            info = component.lstat()
            require(not component.is_symlink() and not
                    (getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT),
                    'Refusing reparse/link path: ' + str(component))
    return path


def inventory(folder, suffix=None, recursive=True):
    folder = safe(folder)
    if not folder.exists():
        return {}
    result = {}
    for directory, dirs, files in os.walk(folder, followlinks=False):
        for name in dirs:
            safe(Path(directory) / name)
        if not recursive:
            dirs.clear()  # Match NeoForge's physical top-level JAR inventory, not Connector caches.
        for name in files:
            path = safe(Path(directory) / name)
            if suffix is None or path.name.lower().endswith(suffix):
                result[path.relative_to(folder).as_posix()] = digest(path.read_bytes())
    return dict(sorted(result.items()))


def java_processes():
    """Image/PID inventory only. Never request command lines, tokens or accounts."""
    require(os.name == 'nt', 'This helper is restricted to the audited Windows pack')
    output = subprocess.run(['tasklist.exe', '/FO', 'CSV', '/NH'], check=True,
                            capture_output=True, text=True, errors='replace', timeout=20)
    return [{'image': row[0], 'pid': row[1]} for row in csv.reader(io.StringIO(output.stdout))
            if len(row) > 1 and row[0].lower() in ('java.exe', 'javaw.exe')]


def default_block(data):
    start = list(re.finditer(rb'(?m)^// kjsgen:start default\r?$', data))
    end = list(re.finditer(rb'(?m)^// kjsgen:end default\r?$', data))
    require(len(start) == len(end) == 1 and start[0].start() < end[0].start(),
            'Expected exactly one ordered native default marker block')
    # Keep every live byte outside the marker lines, including its trailing newline.
    return start[0].start(), end[0].end()


def verify_project(old, new, patch):
    require({k: v for k, v in old.items() if k not in ('recipes', 'removals')} ==
            {k: v for k, v in new.items() if k not in ('recipes', 'removals')},
            'Project options changed outside the selected cards/removals')
    untouched = [r for r in old['recipes'] if r.get('recipeId') not in SELECTED | {RETIRED_CARD}]
    require(len(untouched) == 653 and untouched ==
            [r for r in new['recipes'] if r.get('recipeId') not in SELECTED],
            'The 653 unrelated cards were not preserved exactly and in order')
    selected = [r for r in new['recipes'] if r.get('recipeId') in SELECTED]
    require(len(selected) == 19 and {r['recipeId'] for r in selected} == SELECTED,
            'Missing or duplicated scoped machine cards')
    require(len(new['recipes']) == 672, 'Expected exactly 672 merged cards')
    require(len({r['uid'] for r in new['recipes']}) == 672, 'Duplicate card UUID')
    old_by_id = {r.get('recipeId'): r for r in old['recipes']}
    for card in selected:
        prior = old_by_id.get(card['recipeId'])
        if prior:
            require(prior['uid'] == card['uid'], 'Existing machine card UUID changed')
    require(set(patch['replacedMachineCards'] + patch['addedMachineCards']) == SELECTED and
            len(patch['replacedMachineCards']) == 16 and len(patch['addedMachineCards']) == 3 and
            patch['removedCapstoneCards'] == [RETIRED_CARD], 'Unexpected patch ownership list')
    before, after = old.get('removals', []), new.get('removals', [])
    require(after[:len(before)] == before, 'Existing removal cards changed or reordered')
    added = after[len(before):]
    require(all(r.get('recipeId') in ALLOWED_REMOVALS for r in added) and
            len({r['recipeId'] for r in added}) == len(added), 'Unexpected extra removal rules')


def make_plan(args):
    live, stage = safe(LIVE), safe(args.stage)
    require(stage.is_relative_to(ROOT / 'isolated-runtime') and stage != ROOT / 'isolated-runtime',
            'Stage must be a new project isolated-runtime child')
    require(re.fullmatch(r'[a-z0-9][a-z0-9-]{0,30}', args.revision), 'Unsafe revision')
    guards = {}

    def read(path):
        path = safe(path)
        data = path.read_bytes()
        guards[str(path)] = digest(data)
        return data

    def data(path):
        return json.loads(read(path).decode('utf-8-sig'))

    prep = data(stage / 'lithosphere-preparation.json')
    patch = data(stage / 'material-stage-patch.json')
    require(prep['candidateFileName'] == NEW_JAR and prep['installedJarCount'] == 241 and
            Path(prep['sourcePack']) == live, 'Wrong candidate/source pack preparation')
    require(patch['oldProjectSha256'].lower() == OLD_PROJECT_HASH, 'Unknown live project baseline')
    old_bytes = read(live / PROJECT)
    require(digest(old_bytes) == OLD_PROJECT_HASH == digest(read(stage / 'material-input-backups/default.json')),
            'Live project changed since staging; re-merge and re-test, do not overwrite it')
    new_bytes = read(stage / PROJECT)
    require(digest(new_bytes) == patch['newProjectSha256'].lower(), 'Staged project hash changed')
    verify_project(json.loads(old_bytes.decode('utf-8-sig')),
                   json.loads(new_bytes.decode('utf-8-sig')), patch)

    mods = inventory(live / 'mods', '.jar', recursive=False)
    owned = [name for name in mods if Path(name).name.startswith('industrial_colonies-')]
    require(owned == [OLD_JAR] and mods[OLD_JAR] == OLD_JAR_HASH,
            'Expected exactly the pinned active 0.4.0 JAR; disabled/bak files are not targets')
    expected = {r['name']: r['sha256'].lower() for r in prep['activeMods']
                if r['name'] != NEW_JAR}
    expected.update({r['name']: r['sha256'].lower() for r in prep['heldServerIncompatible']})
    third_party = {k: v for k, v in mods.items() if k != OLD_JAR}
    require(len(third_party) == 240 and third_party == expected,
            'Live third-party JAR inventory differs from the accepted full 241-mod source')
    candidate = read(stage / 'mods' / NEW_JAR)
    with zipfile.ZipFile(io.BytesIO(candidate)) as jar:
        metadata = jar.read('META-INF/neoforge.mods.toml').decode('utf-8')
        require(re.search(r'version\s*=\s*"0\.5\.0"', metadata), 'JAR is not version 0.5.0')
        require('resourcepacks/ic_wwoo_decorative/source_manifest.json' in jar.namelist(),
                'Candidate lacks the embedded WWOO compatibility pack')
        config_defaults = {
            'worldgen/settings.json': 'data/industrial_colonies/geology/settings.json',
            'worldgen/biome_families.json': 'data/industrial_colonies/geology/biome_families.json',
            'worldgen/deposit_families.json': 'data/industrial_colonies/geology/deposit_families.json',
            'worldgen/oil.json': 'data/industrial_colonies/geology/oil.json',
            'processing/manual_cinnabar.json': 'data/industrial_colonies/processing/manual_cinnabar.json'}
        for relative, bundled in config_defaults.items():
            accepted = data(stage / 'config/industrial_colonies' / relative)
            require(accepted == json.loads(jar.read(bundled)), 'Stage IC override differs from candidate: ' + relative)
            target = safe(live / 'config/industrial_colonies' / relative)
            if target.exists():
                require(data(target) == accepted, 'Live IC override differs; review instead of replacing: ' + relative)
    script = read(stage / SCRIPT)
    catalog = read(stage / 'material-processing-catalog.json')
    require(digest(script) == patch['scriptSha256'].lower() and
            digest(catalog) == patch['catalogSha256'].lower(), 'Stage script/catalog not hash-pinned')
    require(not safe(live / SCRIPT).exists(), 'Owned batch script already exists; review a separate upgrade plan')
    exported = read(stage / EXPORT)
    live_export = read(live / EXPORT)
    lo, hi = default_block(live_export)
    slo, shi = default_block(exported)
    merged_export = live_export[:lo] + exported[slo:shi] + live_export[hi:]
    payloads = {str(live / 'mods' / NEW_JAR): candidate, str(live / PROJECT): new_bytes,
                str(live / EXPORT): merged_export, str(live / SCRIPT): script}
    blockers = []
    evidence = {'candidateSha256': digest(candidate), 'catalogSha256': digest(catalog),
                'scriptSha256': digest(script), 'projectSha256': digest(new_bytes),
                'nativeExportSha256': digest(exported), 'materialRevision': args.revision}
    material_path = stage / ('material-processing-report-' + args.revision + '.json')
    export_path = stage / ('material-processing-export-' + args.revision + '.json')
    reports = {}
    for kind, path in [('materialReport', material_path), ('exportReport', export_path)]:
        if not path.exists():
            blockers.append('Missing ' + kind + ': ' + str(path))
            continue
        report = data(path)
        reports[kind] = report
        evidence[kind + 'Sha256'] = guards[str(path)]
        if kind == 'materialReport':
            if not (report.get('status') == 'PASS' and report.get('expectedRecipes') == 299 and
                    report.get('loadedAndVerifiedRecipes') == 299 and not report.get('catalogProblems') and
                    not report.get('failures') and not report.get('fatal') and
                    report.get('sections') and all(str(v).startswith('PASS') for v in report['sections'].values()) and
                    report.get('candidateSha256', '').lower() == digest(candidate) and
                    report.get('catalogSha256', '').lower() == digest(catalog)):
                blockers.append('Material acceptance is not a matching genuine 299/299 PASS')
        else:
            if not (report.get('status') == 'PASS' and report.get('recipeCards') == 672 and
                    report.get('allMergedCardUidsRetained') is True and
                    report.get('projectSha256', '').lower() == digest(new_bytes) and
                    len(report.get('scripts', [])) == 1 and
                    report['scripts'][0].get('sha256', '').lower() == digest(exported)):
                blockers.append('Native project export is not a matching 672-card PASS')
    if ('materialReport' in reports and 'exportReport' in reports and
            reports['materialReport'].get('preScriptProjectExport') != reports['exportReport']):
        blockers.append('Native export differs from the exact export embedded in the material runtime report')
    if args.acceptance:
        acceptance_path = safe(args.acceptance)
        require(acceptance_path.is_relative_to(stage), 'Acceptance receipt must remain inside this stage')
        receipt = data(acceptance_path)
        evidence['lithosphereAcceptanceSha256'] = guards[str(acceptance_path)]
        evidence['lithosphereComparisonSha256'] = digest(canonical(receipt.get('nativeABComparison')))
        base = data(stage / 'preparation.json')
        valid_receipt = (receipt.get('status') == 'PASS' and
                         Path(receipt.get('stage', '')) == stage and
                         receipt.get('candidateSha256', '').lower() == digest(candidate) and
                         receipt.get('sourceCandidateSha256', '').lower() == digest(candidate) and
                         prep['candidateSha256'].lower() == base['candidateSha256'].lower() == digest(candidate) and
                         receipt.get('preparationSha256', '').lower() == guards[str(stage / 'lithosphere-preparation.json')] and
                         receipt.get('basePreparationSha256', '').lower() == guards[str(stage / 'preparation.json')] and
                         receipt.get('expectedTerrainMod') == 'mr_lithosphere' and
                         receipt.get('minimumBuildHeight') == -64 and receipt.get('maximumBuildHeight') == 512 and
                         receipt.get('noiseSettingsSha256', '').lower() == prep['expectedNoiseSha256'].lower() and
                         receipt.get('nativeABComparison', {}).get('status') == 'PASS' and
                         {r.get('order') for r in receipt.get('reports', [])} == {'a', 'b'} and
                         len(receipt.get('reports', [])) == 2)
        if not valid_receipt:
            blockers.append('Lithosphere validator receipt does not bind the current candidate/preparation and passing A/B')
        for entry in receipt.get('reports', []):
            pair = {}
            for kind in ('terrainReport', 'compatibilityReport'):
                path = safe(entry[kind])
                require(path.is_relative_to(stage), 'Receipt references a report outside this stage')
                pair[kind] = data(path)
                require(guards[str(path)] == entry[kind + 'Sha256'].lower(), 'Receipt report hash changed')
            terrain, litho = pair['terrainReport'], pair['compatibilityReport']
            if not (terrain.get('status') == 'PASS' and terrain.get('expectedTerrainMod') == 'mr_lithosphere' and
                    terrain.get('noiseSettingsSha256', '').lower() == prep['expectedNoiseSha256'].lower() and
                    litho.get('status') == 'PASS' and litho.get('economicFeaturesChecked') == 5 and
                    litho.get('directGuardCalls') == 10 and litho.get('minimumBuildHeight') == -64 and
                    litho.get('maximumBuildHeight') == 512 and litho.get('wwooLavaSpringPolicyPreserved') is True and
                    len(litho.get('decorativeResourcePriority', [])) == 12):
                blockers.append('A bound terrain/WWOO compatibility report lacks the required PASS checks')
    else:
        blockers.append('Passing validate-lithosphere-acceptance.ps1 receipt is required before apply')
    if args.client_stage:
        client = safe(args.client_stage)
        require(client.is_relative_to(ROOT / 'isolated-runtime') and client != stage and
                client != ROOT / 'isolated-runtime', 'Client evidence must use its separate project stage')
        client_preparation_path = client / 'material-client-preparation.json'
        cp = data(client_preparation_path)
        require(Path(cp['sourceStage']) == stage and Path(cp['destination']) == client and
                cp['candidateFileName'] == NEW_JAR and cp['stagedJarCount'] == 241 and
                cp['candidateSha256'].lower() == digest(candidate) and
                cp['catalogSha256'].lower() == digest(catalog) and
                cp['mergedProjectSha256'].lower() == digest(new_bytes) and
                cp['materialStagePatchSha256'].lower() == guards[str(stage / 'material-stage-patch.json')],
                'Full-client preparation differs from the current accepted server inputs')
        client_mods = {r['name']: r['sha256'].lower() for r in cp['mods']}
        expected_client_mods = dict(third_party, **{NEW_JAR: digest(candidate)})
        require(len(cp['mods']) == len(client_mods) == 241 and client_mods == expected_client_mods and
                inventory(client / 'mods', '.jar', recursive=False) == client_mods,
                'Full-client 241-JAR manifest or physical bytes differ')
        require(digest(read(client / 'material-client-inputs/catalog.json')) == digest(catalog) and
                digest(read(client / 'material-client-inputs/content.json')) == cp['contentSha256'].lower(),
                'Client content/catalog snapshot changed')
        require(digest(read(client / PROJECT)) == digest(new_bytes) and
                digest(read(client / SCRIPT)) == digest(script), 'Client project/owned policy differs from server stage')
        evidence['clientPreparationSha256'] = guards[str(client_preparation_path)]
        evidence['clientModManifestSha256'] = digest(canonical(client_mods))
        client_report_path = client / 'material-client-report.json'
        if not client_report_path.exists():
            blockers.append('Full-client native GPU report is not available yet')
        else:
            cr = data(client_report_path)
            evidence['clientReportSha256'] = guards[str(client_report_path)]
            if not (cr.get('status') == 'PASS' and not cr.get('error') and
                    cr.get('candidateSha256', '').lower() == digest(candidate) and
                    cr.get('catalogSha256', '').lower() == digest(catalog) and
                    cr.get('contentSha256', '').lower() == cp['contentSha256'].lower() and
                    cr.get('physicalInputJars') == 241 and cr.get('catalogRecipes') == 299 and
                    cr.get('geologyQuads') == 258 and len(cr.get('geologyModels', [])) == 41 and
                    len(cr.get('materialItemModels', [])) == 74 and len(cr.get('tankFluidSprites', [])) == 25 and
                    cr.get('fluidSpriteChecks') == 50 and cr.get('renderedFrames', 0) >= 480 and
                    cr.get('radianceRuntimeApplicability', {}).get('refinedRadianceBranchReturnsFalse') is True):
                blockers.append('Full-client native rendering acceptance is not a matching complete PASS')
            required_shots = {'01-geology-blocks.png', '02-material-items-a.png',
                              '03-material-items-b.png', '04-tank-fluids.png'}
            shots = cr.get('screenshots', [])
            if len(shots) != 4 or {Path(s['path']).name for s in shots} != required_shots:
                blockers.append('Full-client evidence must include the four native framebuffer captures')
            for shot in shots:
                path = safe(shot['path'])
                require(path.parent == client / 'material-client-screenshots', 'Screenshot path escaped exact evidence folder')
                png = read(path)
                require(digest(png) == shot['sha256'].lower() and png[:8] == b'\x89PNG\r\n\x1a\n' and
                        png[12:16] == b'IHDR' and int.from_bytes(png[16:20], 'big') == shot['width'] > 0 and
                        int.from_bytes(png[20:24], 'big') == shot['height'] > 0 and shot['frames'] >= 120,
                        'Framebuffer screenshot hash/dimensions do not match native client report')
    else:
        blockers.append('--client-stage with a matching complete full-client PASS is required before apply')
    configs = inventory(live / 'config')
    defaults = inventory(live / 'defaultconfigs')
    stage_configs = inventory(stage / 'config')
    # Only audit differences. No test-generated config, defaultconfig, or world is a write target.
    config_differences = [{'path': k, 'live': configs.get(k), 'stage': stage_configs.get(k)}
                          for k in sorted(configs.keys() | stage_configs.keys())
                          if configs.get(k) != stage_configs.get(k)]
    for key in ['wwoo', 'lithostitched.json', 'modernfoundry-common.toml', 'tfmg-common.toml', 'tfmg-server.toml']:
        require({k: v for k, v in configs.items() if k == key or k.startswith(key + '/')} ==
                {k: v for k, v in stage_configs.items() if k == key or k.startswith(key + '/')},
                'Relevant live/stage config differs: ' + key)
    scripts = inventory(live / 'kubejs')
    plan = {'schema': 1, 'kind': 'scoped-material-lithosphere-0.5', 'stage': str(stage), 'live': str(live),
            'evidence': evidence, 'blockers': blockers, 'unrelatedCardsPreserved': 653,
            'selectedMachineCards': sorted(SELECTED), 'retiredCard': RETIRED_CARD,
            'retireJar': {'path': str(live / 'mods' / OLD_JAR), 'sha256': OLD_JAR_HASH},
            'writes': [{'path': path, 'before': digest(Path(path).read_bytes()) if Path(path).exists() else None,
                        'after': digest(value), 'bytes': len(value)} for path, value in payloads.items()],
            'inputGuards': guards, 'thirdPartyMods': third_party,
            'thirdPartyModManifestSha256': digest(canonical(third_party)),
            'preservedConfig': configs, 'preservedDefaultconfigs': defaults,
            'preservedKubejs': {k: v for k, v in scripts.items() if k not in
                               ('server_scripts/kjsgen_recipes.js', 'server_scripts/zz_industrial_material_processing.js')},
            'configDifferencesNotDeployed': config_differences,
            'saves': 'Not enumerated, copied, opened, modified or migrated',
            'outerKubejsBytesPreserved': True}
    return plan, payloads


def atomic_write(path, value):
    path = safe(path)
    require(path.parent.is_dir(), 'Missing exact target parent: ' + str(path.parent))
    fd, temporary = tempfile.mkstemp(prefix='.ic-deploy-', suffix='.tmp', dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()  # Only this exact helper-owned temporary file.


def expect_target(path, expected):
    path = safe(path)
    actual = digest(path.read_bytes()) if path.exists() else None
    require(actual == expected, 'Target changed immediately before installation; preserve it: ' + str(path))


def apply_plan(args, plan, payloads):
    require(not plan['blockers'], 'Refusing apply: ' + '; '.join(plan['blockers']))
    require(args.expected_plan_sha256 and args.expected_plan_sha256.lower() == digest(canonical(plan)),
            '--expected-plan-sha256 must equal the reviewed dry-run plan')
    require(not java_processes(), 'Close all Java/Javaw processes before deployment; no override is provided')
    live = safe(plan['live'])
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup = safe(live / '_industrial_colonies_backups' / ('material-lithosphere-0.5-' + stamp))
    backup.mkdir(parents=True, exist_ok=False)
    journal = {'status': 'BACKING_UP', 'planSha256': digest(canonical(plan)), 'plan': plan,
               'backupDirectory': str(backup), 'written': [], 'retiredJarMoved': False}
    before = {}
    for entry in plan['writes'] + [dict(path=plan['retireJar']['path'], before=OLD_JAR_HASH)]:
        target = safe(entry['path'])
        if entry['before'] is not None:
            value = target.read_bytes()
            require(digest(value) == entry['before'], 'Target changed before backup: ' + str(target))
            saved = backup / 'before' / target.relative_to(live)
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(value)
            require(digest(saved.read_bytes()) == entry['before'], 'Backup verification failed')
            before[str(target)] = value
    evidence_dir = backup / 'evidence'
    evidence_dir.mkdir()
    for path, expected in plan['inputGuards'].items():
        source = safe(path)
        if (source.is_relative_to(ROOT / 'isolated-runtime') and source.suffix == '.json' and
                source.parent != Path(plan['stage']) / 'config/industrial_colonies/worldgen'):
            value = source.read_bytes()
            require(digest(value) == expected, 'Evidence changed while backing up')
            target = evidence_dir / source.relative_to(ROOT / 'isolated-runtime')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
    # Catalog provenance is archived here only, never installed to an invented runtime path.
    atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
    fresh_plan, fresh_payloads = make_plan(args)
    require(fresh_plan == plan and fresh_payloads == payloads and not java_processes(),
            'Inputs or processes changed after backup; no installation was performed')
    retired = backup / 'retired' / OLD_JAR
    retired.parent.mkdir()
    try:
        # Remove the old active JAR recoverably, then install only the four listed payloads.
        expect_target(plan['retireJar']['path'], OLD_JAR_HASH)
        journal['status'] = 'INSTALLING'
        journal['retirementIntent'] = True
        atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
        shutil.move(plan['retireJar']['path'], retired)
        journal['retiredJarMoved'] = True
        atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
        for entry in plan['writes']:
            path = safe(entry['path'])
            expect_target(path, entry['before'])
            # Journal before attempting replacement so interrupted/failed writes are recoverable.
            journal['written'].append(str(path))
            atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
            atomic_write(path, payloads[str(path)])
            require(digest(path.read_bytes()) == entry['after'], 'Installed hash mismatch')
            atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
        require(inventory(live / 'config') == plan['preservedConfig'] and
                inventory(live / 'defaultconfigs') == plan['preservedDefaultconfigs'], 'Config changed during deployment')
        expected_mods = dict(plan['thirdPartyMods'], **{NEW_JAR: plan['evidence']['candidateSha256']})
        require(inventory(live / 'mods', '.jar', recursive=False) == expected_mods, 'Unexpected active mod inventory after deployment')
        after_scripts = inventory(live / 'kubejs')
        require({k: v for k, v in after_scripts.items() if k not in
                 ('server_scripts/kjsgen_recipes.js', 'server_scripts/zz_industrial_material_processing.js')} ==
                plan['preservedKubejs'], 'Unrelated KubeJS file changed during deployment')
        journal['status'] = 'APPLIED'
        atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
    except BaseException as failure:
        journal['status'] = 'ROLLING_BACK'
        journal['failure'] = str(failure)
        try:
            for path in reversed(journal['written']):
                target = safe(path)
                original = digest(before[path]) if path in before else None
                present = digest(target.read_bytes()) if target.exists() else None
                if present == original:
                    continue  # A journaled write was never committed, or was already restored.
                require(present == digest(payloads[path]),
                        'Concurrent target edit preserved; manual recovery required: ' + str(target))
                retained = backup / 'failed-new' / target.relative_to(live)
                retained.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    shutil.move(str(target), retained)
                if path in before:
                    atomic_write(target, before[path])
            if retired.exists():
                require(digest(retired.read_bytes()) == OLD_JAR_HASH, 'Retired backup changed; preserve it for manual review')
                require(not Path(plan['retireJar']['path']).exists(), 'Old JAR target unexpectedly occupied')
                shutil.move(retired, plan['retireJar']['path'])
            journal['status'] = 'ROLLED_BACK'
        except BaseException as rollback_failure:
            journal['status'] = 'MANUAL_RECOVERY_REQUIRED'
            journal['rollbackFailure'] = str(rollback_failure)
        atomic_write(backup / 'deployment.json', json.dumps(journal, indent=2).encode('utf-8'))
        raise RuntimeError('Deployment failed; inspect ' + str(backup / 'deployment.json')) from failure
    print(json.dumps({'status': journal['status'], 'backup': str(backup), 'liveWrites': True}, indent=2))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--stage', type=Path, default=DEFAULT_STAGE)
    parser.add_argument('--revision', required=True, help='Exact accepted material/export revision, e.g. a4')
    parser.add_argument('--acceptance', type=Path, help='Output of validate-lithosphere-acceptance.ps1')
    parser.add_argument('--client-stage', type=Path, help='Separate accepted 241-JAR material-client stage')
    parser.add_argument('--apply', action='store_true', help='Explicit live deployment; default is read-only')
    parser.add_argument('--expected-plan-sha256')
    args = parser.parse_args()
    plan, payloads = make_plan(args)
    if args.apply:
        apply_plan(args, plan, payloads)
    else:
        process_error = None
        try:
            processes = java_processes()
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            processes = None
            process_error = str(error)  # Unavailable is never interpreted as no running Java.
        print(json.dumps({'mode': 'DRY_RUN', 'liveWrites': False, 'javaProcesses': processes,
                          'javaInspectionError': process_error,
                          'applyReady': process_error is None and not processes and not plan['blockers'],
                          'planSha256': digest(canonical(plan)), 'plan': plan}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
