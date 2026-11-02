"""Only the three user-requested dirty pair-alloy intermediates; no recipes or fluids."""

DIRTY_ALLOY_ITEMS = (('dirty_vibranium_allthemodium_alloy_dust', 'Dirty Allthemodium–Vibranium Alloy Dust', 'allthemodium:item/dirty_vibranium_dust'), ('dirty_unobtainium_allthemodium_alloy_dust', 'Dirty Allthemodium–Unobtainium Alloy Dust', 'allthemodium:item/dirty_allthemodium_dust'), ('dirty_unobtainium_vibranium_alloy_dust', 'Dirty Vibranium–Unobtainium Alloy Dust', 'allthemodium:item/dirty_unobtainium_dust'))

def register_items(builder):
    for name, label, texture in DIRTY_ALLOY_ITEMS:
        builder.item(name, label=label, texture=texture)
