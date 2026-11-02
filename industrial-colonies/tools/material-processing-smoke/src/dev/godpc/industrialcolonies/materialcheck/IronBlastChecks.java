package dev.godpc.industrialcolonies.materialcheck;

import com.drmangotea.tfmg.content.machinery.metallurgy.blast_furnace.BlastFurnaceOutputBlockEntity;
import com.drmangotea.tfmg.recipes.IndustrialBlastingRecipe;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

/** Native recipe lookup and completion; timing/structure assembly are fixture-controlled. */
public final class IronBlastChecks {
    public static void run(GameTestHelper h) {
        check(h,"iron/blast_reduction","industrial_colonies:iron_bearing_dust","iron",8);
        check(h,"iron/blast_raw","minecraft:raw_iron","iron",100);
        check(h,"gold/blast_raw","minecraft:raw_gold","gold",25);
        System.out.println("IRON_BLAST_PASS machine=TFMG rawIron=100 dustIron=8 rawGold=25 fuel=required nativeCompletion=PASS");
    }
    private static void check(GameTestHelper h,String path,String feed,String metal,int amount) {
        var id=ResourceLocation.parse("industrial_colonies:processing/"+path);
        var recipe=h.getLevel().getRecipeManager().byKey(id).orElseThrow().value();
        h.assertTrue(recipe instanceof IndustrialBlastingRecipe,"Iron reduction still belongs to another machine");
        var blast=(IndustrialBlastingRecipe)recipe;
        h.assertTrue(blast.getProcessingDuration()==30,"TFMG seconds were confused with IE ticks");
        var pos=new BlockPos(2,3,2);
        h.setBlock(pos,BuiltInRegistries.BLOCK.get(ResourceLocation.parse("tfmg:blast_furnace_output")));
        var fixture=(BlastFurnaceOutputBlockEntity)h.getBlockEntity(pos);
        var furnace=new BlastFurnaceOutputBlockEntity(fixture.getType(),fixture.getBlockPos(),fixture.getBlockState()) {
            @Override public int getSize(){return 3;}
        };
        furnace.setLevel(h.getLevel());
        furnace.inputInventory.setStackInSlot(0,new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(feed))));
        furnace.executeRecipe();
        h.assertTrue(furnace.timer>0&&furnace.timer<=600,"Native furnace did not find/start the iron recipe");
        furnace.timer=0;furnace.fuel=0;furnace.tick();
        h.assertTrue(furnace.primaryTank.isEmpty()&&!furnace.inputInventory.getStackInSlot(0).isEmpty(),"Iron processing bypasses fuel");
        furnace.fuel=1;furnace.tick();
        h.assertTrue(furnace.inputInventory.getStackInSlot(0).isEmpty(),"Native furnace did not consume dust");
        h.assertTrue(furnace.primaryTank.getFluidAmount()==amount&&BuiltInRegistries.FLUID.getKey(furnace.primaryTank.getFluid().getFluid()).toString().equals("modernfoundry:molten_"+metal),"Iron output changed");
        h.assertTrue(furnace.secondaryTank.getFluidAmount()==10&&BuiltInRegistries.FLUID.getKey(furnace.secondaryTank.getFluid().getFluid()).toString().equals("tfmg:molten_slag"),"Slag output missing");
        h.setBlock(pos,net.minecraft.world.level.block.Blocks.AIR);

    }
}
