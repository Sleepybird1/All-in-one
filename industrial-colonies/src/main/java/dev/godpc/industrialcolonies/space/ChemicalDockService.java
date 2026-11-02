package dev.godpc.industrialcolonies.space;

import mekanism.api.chemical.IChemicalHandler;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import dev.ryanhcode.sable.Sable;

/** Explicit operator binding; capacity and persistent cargo remain exclusively in native tanks. */
public final class ChemicalDockService {
    private static final String KEY="industrial_colonies_chemical_dock";
    private static final ResourceLocation DOCK=ResourceLocation.parse("simulated:docking_connector");
    public record Binding(Direction offset,Direction tankSide,Direction portSide) {}
    private ChemicalDockService() {}

    public static void register(IEventBus bus) {
        bus.addListener(ChemicalDockService::capabilities);
        NeoForge.EVENT_BUS.addListener(ChemicalDockService::commands);
    }
    public static void capabilities(RegisterCapabilitiesEvent event) {
        if(BuiltInRegistries.BLOCK.containsKey(DOCK))event.registerBlock(mekanism.common.capabilities.Capabilities.CHEMICAL.block(),
            (level,pos,state,be,side)->be==null?null:view(be,side),BuiltInRegistries.BLOCK.get(DOCK));
    }
    public static Binding binding(BlockEntity dock) {
        var tag=dock.getPersistentData().getCompound(KEY);
        if(tag.getInt("format")!=1)return null;
        Direction offset=Direction.byName(tag.getString("offset")),tank=Direction.byName(tag.getString("tankSide")),port=Direction.byName(tag.getString("portSide"));
        return offset==null||tank==null||port==null?null:new Binding(offset,tank,port);
    }
    public static void bind(BlockEntity dock,Binding binding) {
        if(!(dock.getLevel() instanceof ServerLevel level)||!level.getServer().isSameThread()||!(dock instanceof ChemicalDockAccess))throw new IllegalArgumentException("Loaded server dock required");
        if(tank(dock,binding)==null)throw new IllegalArgumentException("Selected adjacent position must be a loaded native Mekanism chemical tank with access on the selected tank face");
        invalidate(dock);var tag=new CompoundTag();tag.putInt("format",1);tag.putString("offset",binding.offset().getName());tag.putString("tankSide",binding.tankSide().getName());tag.putString("portSide",binding.portSide().getName());
        dock.getPersistentData().put(KEY,tag);dock.setChanged();
    }
    public static void unbind(BlockEntity dock) {invalidate(dock);dock.getPersistentData().remove(KEY);dock.setChanged();}
    public static void invalidate(BlockEntity dock) {
        if(dock instanceof ChemicalDockAccess access)access.ic$revokeChemical();
        if(dock.getLevel()!=null&&!dock.getLevel().isClientSide)dock.getLevel().invalidateCapabilities(dock.getBlockPos());
    }
    /** Native pair maintenance may repeat a stable lock callback; do not churn capability caches. */
    public static void beforeSetDock(BlockEntity dock,Object nextPeer,boolean locked) {
        if(locked&&nextPeer instanceof BlockEntity other&&peer(dock)==other) {
            try {if((Boolean)dock.getClass().getMethod("isLocked").invoke(dock))return;}
            catch(ReflectiveOperationException|ClassCastException ignored) { }
        }
        invalidate(dock);
    }
    private static boolean loaded(BlockEntity be) {
        return be!=null&&!be.isRemoved()&&be.getLevel() instanceof ServerLevel level&&level.getServer().isSameThread()
            &&level.hasChunkAt(be.getBlockPos())&&level.getBlockEntity(be.getBlockPos())==be;
    }
    private static BlockEntity peer(BlockEntity dock) {
        if(!loaded(dock))return null;
        try {
            var pos=(BlockPos)dock.getClass().getField("otherConnectorPosition").get(dock);
            if(pos==null||!dock.getLevel().hasChunkAt(pos))return null;
            return (BlockEntity)dock.getClass().getMethod("getOtherConnector").invoke(dock);
        }catch(ReflectiveOperationException|ClassCastException failure){return null;}
    }
    private static boolean allowed(BlockEntity dock) {
        if(!loaded(dock))return false;
        var level=(ServerLevel)dock.getLevel();
        if(AutonomousShipControl.get(level.getServer()).allDisabled())return false;
        var body=Sable.HELPER.getContaining(dock);
        return !(body instanceof dev.ryanhcode.sable.sublevel.ServerSubLevel ship)||!SpaceflightAuthorization.automationDisabled(ship);
    }
    private static boolean pair(BlockEntity a,BlockEntity b) {
        if(!allowed(a)||!allowed(b)||a.getLevel()!=b.getLevel()||!(b instanceof ChemicalDockAccess)||peer(a)!=b||peer(b)!=a)return false;
        try{return (Boolean)a.getClass().getMethod("isLocked").invoke(a)&&(Boolean)b.getClass().getMethod("isLocked").invoke(b);}
        catch(ReflectiveOperationException|ClassCastException failure){return false;}
    }
    private static BlockEntity tank(BlockEntity dock,Binding binding) {
        if(binding==null||!loaded(dock))return null;
        var level=(ServerLevel)dock.getLevel();var pos=dock.getBlockPos().relative(binding.offset());
        if(!level.hasChunkAt(pos))return null;
        var be=level.getBlockEntity(pos);if(be==null||!loaded(be))return null;
        var id=BuiltInRegistries.BLOCK_ENTITY_TYPE.getKey(be.getType());
        if(id==null||!id.getNamespace().equals("mekanism")||!id.getPath().endsWith("chemical_tank"))return null;
        if(Sable.HELPER.getContaining(be)!=Sable.HELPER.getContaining(dock))return null;
        return level.getCapability(mekanism.common.capabilities.Capabilities.CHEMICAL.block(),pos,binding.tankSide())==null?null:be;
    }
    public static IChemicalHandler view(BlockEntity dock,Direction side) {
        if(!(dock instanceof ChemicalDockAccess access)||!loaded(dock))return null;
        var binding=binding(dock);if(binding==null||side!=binding.portSide())return null;
        var lease=access.ic$chemicalLease();
        if(lease!=null&&lease.resolve()!=null)return lease.view;
        // Creating/replacing a view is not a physical link transition. Bumping the
        // epoch here makes the opposite port revoke this view as it opens its own.
        if(lease!=null)lease.view.revoke();
        access.ic$chemicalLease(null);
        var peer=peer(dock);
        if(peer==null||!pair(dock,peer)||tank(dock,binding)==null)return null;
        var remoteBinding=binding(peer);var remote=tank(peer,remoteBinding);if(remote==null)return null;
        lease=new Lease(dock,peer,remote,binding,remoteBinding);access.ic$chemicalLease(lease);return lease.view;
    }
    public static final class Lease {
        private final BlockEntity local,peer,remoteTank,localTank;
        private final Binding localBinding,remoteBinding;
        private final long localEpoch,remoteEpoch,controlRevision;
        private final AutonomousShipControl controls;
        private final IChemicalHandler targetHandler;
        public final ChemicalDockView view;
        Lease(BlockEntity local,BlockEntity peer,BlockEntity tank,Binding localBinding,Binding remoteBinding) {
            this.local=local;this.peer=peer;this.remoteTank=tank;this.localBinding=localBinding;this.remoteBinding=remoteBinding;this.localTank=tank(local,localBinding);
            localEpoch=((ChemicalDockAccess)local).ic$chemicalEpoch();remoteEpoch=((ChemicalDockAccess)peer).ic$chemicalEpoch();
            controls=AutonomousShipControl.get(((ServerLevel)local.getLevel()).getServer());controlRevision=controls.chemicalDockRevision();
            targetHandler=((ServerLevel)peer.getLevel()).getCapability(mekanism.common.capabilities.Capabilities.CHEMICAL.block(),tank.getBlockPos(),remoteBinding.tankSide());
            view=new ChemicalDockView(this::resolve);
        }
        IChemicalHandler resolve() {
            boolean valid=loaded(local)&&loaded(peer)&&localEpoch==((ChemicalDockAccess)local).ic$chemicalEpoch()&&remoteEpoch==((ChemicalDockAccess)peer).ic$chemicalEpoch()
                &&controlRevision==controls.chemicalDockRevision()&&pair(local,peer)&&localBinding.equals(binding(local))&&remoteBinding.equals(binding(peer))
                &&tank(local,localBinding)==localTank&&tank(peer,remoteBinding)==remoteTank;
            if(!valid){view.revoke();return null;}
            var current=((ServerLevel)peer.getLevel()).getCapability(mekanism.common.capabilities.Capabilities.CHEMICAL.block(),remoteTank.getBlockPos(),remoteBinding.tankSide());
            if(current==null||current!=targetHandler){view.revoke();return null;}
            return current;
        }
    }
    private static void commands(RegisterCommandsEvent event) {
        var root=Commands.literal("icchemicaldock").requires(s->s.hasPermission(4));
        root.then(Commands.literal("unbind").then(Commands.argument("dock",BlockPosArgument.blockPos()).executes(c->{var be=c.getSource().getLevel().getBlockEntity(BlockPosArgument.getLoadedBlockPos(c,"dock"));if(!(be instanceof ChemicalDockAccess))return 0;unbind(be);return 1;})));
        root.then(Commands.literal("bind").then(Commands.argument("dock",BlockPosArgument.blockPos()).then(Commands.argument("tank_offset",StringArgumentType.word()).then(Commands.argument("tank_face",StringArgumentType.word()).then(Commands.argument("port_face",StringArgumentType.word()).executes(c->{
            try {var offset=Direction.byName(StringArgumentType.getString(c,"tank_offset"));var tank=Direction.byName(StringArgumentType.getString(c,"tank_face"));var port=Direction.byName(StringArgumentType.getString(c,"port_face"));
                if(offset==null||tank==null||port==null)throw new IllegalArgumentException("Use north, south, east, west, up or down for each direction");
                var be=c.getSource().getLevel().getBlockEntity(BlockPosArgument.getLoadedBlockPos(c,"dock"));if(be==null)throw new IllegalArgumentException("Loaded dock required");
                bind(be,new Binding(offset,tank,port));c.getSource().sendSuccess(()->Component.literal("Chemical dock bound to the selected adjacent native tank. Transfer requires a reciprocal locked and configured dock."),true);return 1;
            }catch(IllegalArgumentException failure){c.getSource().sendFailure(Component.literal(failure.getMessage()));return 0;}
        }))))));event.getDispatcher().register(root);
    }
}
