// Applied Create normally lets any early Create shaft or cog attune an ME P2P
// tunnel to stress. Keep the feature, but make the manufactured ME Gearbox the
// deliberate key so remote kinetic transport cannot bypass its gateway recipe.
ServerEvents.tags('item', event => {
  const stressAttunement = 'appliedcreate:p2p_attunements/stress_p2p_tunnel'
  event.removeAll(stressAttunement)
  event.add(stressAttunement, 'appliedcreate:me_gearbox')
})
