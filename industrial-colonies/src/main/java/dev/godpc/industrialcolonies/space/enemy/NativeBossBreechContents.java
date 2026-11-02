package dev.godpc.industrialcolonies.space.enemy;

import net.minecraft.world.item.ItemStack;
import rbasamoyai.createbigcannons.cannons.autocannon.breech.AbstractAutocannonBreechBlockEntity;
import java.util.*;

/** Defensive item snapshots only, not arbitrary block-entity NBT conservation. */
public final class NativeBossBreechContents {
 private final List<ItemStack> input;
 private final ItemStack output,magazine;
 private NativeBossBreechContents(AbstractAutocannonBreechBlockEntity breech){
  if(breech.getInputBuffer().size()>256)throw new IllegalStateException("Unbounded breech queue");
  input=breech.getInputBuffer().stream().map(s->Objects.requireNonNull(s).copy()).toList();
  output=Objects.requireNonNull(breech.getOutputBuffer()).copy();
  magazine=Objects.requireNonNull(breech.getMagazine()).copy();
 }
 public static NativeBossBreechContents capture(AbstractAutocannonBreechBlockEntity breech){return new NativeBossBreechContents(breech);}
 public boolean matches(AbstractAutocannonBreechBlockEntity breech){
  if(breech.getInputBuffer().size()!=input.size()||breech.getOutputBuffer()==null||breech.getMagazine()==null
      ||!ItemStack.matches(output,breech.getOutputBuffer())||!ItemStack.matches(magazine,breech.getMagazine()))return false;
  var actual=breech.getInputBuffer().iterator();
  for(var expected:input){var stack=actual.next();if(stack==null||!ItemStack.matches(expected,stack))return false;}
  return true;
 }
}
