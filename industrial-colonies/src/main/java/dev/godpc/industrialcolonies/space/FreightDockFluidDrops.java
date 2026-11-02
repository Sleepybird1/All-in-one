package dev.godpc.industrialcolonies.space;

import java.util.Set;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.*;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.level.BlockDropsEvent;

/** Preserve the native fluid in the existing connector drop. Native onRemove
 * already drops inventory separately: never copy inventory, commission, peer,
 * position, schedule or body identity into the item. No replacement drops. */
@EventBusSubscriber(modid="industrial_colonies")
public final class FreightDockFluidDrops {
 private static final String ID="simulated:docking_connector";
 private FreightDockFluidDrops(){}
 static CompoundTag payload(CompoundTag saved){
  if(!saved.getString("id").equals(ID)||!saved.contains("Tank",Tag.TAG_COMPOUND))throw new IllegalArgumentException("Exact native connector tank required");
  var tank=saved.getCompound("Tank");
  if(!tank.getAllKeys().equals(Set.of("Amount","Variant"))||!tank.contains("Amount",Tag.TAG_LONG)||!tank.contains("Variant",Tag.TAG_COMPOUND))throw new IllegalArgumentException("Unsupported connector tank schema");
  long amount=tank.getLong("Amount");if(amount<0||amount>1000)throw new IllegalArgumentException("Native connector capacity exceeded");
  if(amount==0)return new CompoundTag();
  var variant=tank.getCompound("Variant");String fluid=variant.getString("Fluid");
  if(!variant.getAllKeys().equals(Set.of("Fluid","data"))||!variant.contains("Fluid",Tag.TAG_STRING)||!variant.contains("data",Tag.TAG_COMPOUND)||!fluid.matches("[a-z0-9_.-]+:[a-z0-9/._-]+")||fluid.equals("minecraft:empty"))throw new IllegalArgumentException("Complete nonempty native fluid variant required");
  var result=new CompoundTag();result.putString("id",ID);result.put("Tank",tank.copy());return result;
 }
 @SubscribeEvent
 public static void dropped(BlockDropsEvent event){
  var be=event.getBlockEntity();
  if(be==null||!BuiltInRegistries.BLOCK.getKey(event.getState().getBlock()).toString().equals(ID)||!be.getClass().getName().equals("dev.simulated_team.simulated.content.blocks.docking_connector.DockingConnectorBlockEntity"))return;
  var matches=event.getDrops().stream().filter(e->BuiltInRegistries.ITEM.getKey(e.getItem().getItem()).toString().equals(ID)).toList();
  // A suppressed/modified loot result must not be replaced or multiplied.
  if(matches.size()!=1||matches.getFirst().getItem().getCount()!=1)return;
  var stack=matches.getFirst().getItem();if(stack.has(DataComponents.BLOCK_ENTITY_DATA))return;
  var data=payload(be.saveWithFullMetadata(event.getLevel().registryAccess()));if(data.isEmpty())return;
  stack.set(DataComponents.BLOCK_ENTITY_DATA,CustomData.of(data));
 }
}
