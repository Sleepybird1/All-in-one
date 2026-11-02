package dev.godpc.industrialcolonies.space;

import appeng.api.networking.*;
import dev.ryanhcode.sable.Sable;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;

/** Staged physical bridge prototype. Native AE nodes retain all inventory/crafting custody. */
public final class AeDockService {
    private static final String KEY="industrial_colonies_ae_dock";
    public record Binding(Direction offset,Direction face) {}
    private AeDockService() {}
    /** Operator-only prototype setup; this is not the deferred survival acquisition recipe. */
    public static void register(){net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(AeDockService::commands);}
    private static void commands(net.neoforged.neoforge.event.RegisterCommandsEvent event) {
        var root=net.minecraft.commands.Commands.literal("icaedock").requires(s->s.hasPermission(4));
        root.then(net.minecraft.commands.Commands.literal("unbind").then(net.minecraft.commands.Commands.argument("dock",net.minecraft.commands.arguments.coordinates.BlockPosArgument.blockPos()).executes(c->{
            var dock=c.getSource().getLevel().getBlockEntity(net.minecraft.commands.arguments.coordinates.BlockPosArgument.getLoadedBlockPos(c,"dock"));
            if(!(dock instanceof AeDockAccess))return 0;unbind(dock);return 1;
        })));
        root.then(net.minecraft.commands.Commands.literal("bind").then(net.minecraft.commands.Commands.argument("dock",net.minecraft.commands.arguments.coordinates.BlockPosArgument.blockPos())
            .then(net.minecraft.commands.Commands.argument("node_offset",com.mojang.brigadier.arguments.StringArgumentType.word())
            .then(net.minecraft.commands.Commands.argument("node_face",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->{
                try {
                    var offset=Direction.byName(com.mojang.brigadier.arguments.StringArgumentType.getString(c,"node_offset"));
                    var face=Direction.byName(com.mojang.brigadier.arguments.StringArgumentType.getString(c,"node_face"));
                    if(offset==null||face==null)throw new IllegalArgumentException("Use north, south, east, west, up or down");
                    var dock=c.getSource().getLevel().getBlockEntity(net.minecraft.commands.arguments.coordinates.BlockPosArgument.getLoadedBlockPos(c,"dock"));
                    bind(dock,new Binding(offset,face));c.getSource().sendSuccess(()->net.minecraft.network.chat.Component.literal("AE dock bound. Native ME access requires both configured docks to remain physically locked."),true);return 1;
                }catch(IllegalArgumentException failure){c.getSource().sendFailure(net.minecraft.network.chat.Component.literal(failure.getMessage()));return 0;}
            })))));
        event.getDispatcher().register(root);
    }
    public static Binding binding(BlockEntity dock) {
        var tag=dock.getPersistentData().getCompound(KEY);
        if(tag.getInt("format")!=1)return null;
        var offset=Direction.byName(tag.getString("offset"));var face=Direction.byName(tag.getString("face"));
        return offset==null||face==null?null:new Binding(offset,face);
    }
    public static void bind(BlockEntity dock,Binding binding) {
        if(!(dock instanceof AeDockAccess)||node(dock,binding)==null)throw new IllegalArgumentException("Loaded dock and adjacent exposed native AE node required");
        invalidate(dock);var tag=new CompoundTag();tag.putInt("format",1);tag.putString("offset",binding.offset().getName());tag.putString("face",binding.face().getName());
        dock.getPersistentData().put(KEY,tag);dock.setChanged();
    }
    public static void unbind(BlockEntity dock){invalidate(dock);dock.getPersistentData().remove(KEY);dock.setChanged();}
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
        }catch(ReflectiveOperationException|ClassCastException e){return null;}
    }
    private static boolean allowed(BlockEntity dock) {
        if(!loaded(dock))return false;
        if(AutonomousShipControl.get(((ServerLevel)dock.getLevel()).getServer()).allDisabled())return false;
        var body=Sable.HELPER.getContaining(dock);
        return !(body instanceof dev.ryanhcode.sable.sublevel.ServerSubLevel ship)||!SpaceflightAuthorization.automationDisabled(ship);
    }
    private static boolean pair(BlockEntity a,BlockEntity b) {
        if(!allowed(a)||!allowed(b)||!(b instanceof AeDockAccess)||a.getLevel()!=b.getLevel()||peer(a)!=b||peer(b)!=a)return false;
        try{return (Boolean)a.getClass().getMethod("isLocked").invoke(a)&&(Boolean)b.getClass().getMethod("isLocked").invoke(b);}
        catch(ReflectiveOperationException|ClassCastException e){return false;}
    }
    private static IGridNode node(BlockEntity dock,Binding binding) {
        if(binding==null||!loaded(dock))return null;
        var level=(ServerLevel)dock.getLevel();var pos=dock.getBlockPos().relative(binding.offset());
        if(!level.hasChunkAt(pos))return null;
        var be=level.getBlockEntity(pos);
        if(!loaded(be)||Sable.HELPER.getContaining(be)!=Sable.HELPER.getContaining(dock))return null;
        return GridHelper.getExposedNode(level,pos,binding.face());
    }
    public static void invalidate(BlockEntity dock) {
        if(dock instanceof AeDockAccess access&&access.ic$aeLink()!=null)access.ic$aeLink().destroy();
    }
    public static void beforeSetDock(BlockEntity dock,Object next,boolean locked) {
        if(locked&&next instanceof BlockEntity other&&pair(dock,other))return;
        invalidate(dock);
    }
    public static void refresh(BlockEntity dock) {
        if(!(dock instanceof AeDockAccess access))return;
        if(!dock.getPersistentData().contains(KEY)){invalidate(dock);return;}
        if(!loaded(dock))return;
        var old=access.ic$aeLink();
        if(old!=null){if(old.valid())return;old.destroy();}
        var other=peer(dock);if(other==null||!pair(dock,other))return;
        var remote=(AeDockAccess)other;
        if(remote.ic$aeLink()!=null){if(remote.ic$aeLink().valid())return;remote.ic$aeLink().destroy();}
        var a=node(dock,binding(dock));var b=node(other,binding(other));
        if(a==null||b==null||a==b)return;
        // Never adopt or destroy an existing edge owned by a different connector.
        for(var connection:a.getConnections())if(connection.getOtherSide(a)==b)return;
        var link=new Link(dock,other,a,b,GridHelper.createConnection(a,b));
        access.ic$aeLink(link);remote.ic$aeLink(link);
    }
    public static final class Link {
        final BlockEntity aDock,bDock;final IGridNode a,b;final IGridConnection connection;boolean destroyed;
        Link(BlockEntity aDock,BlockEntity bDock,IGridNode a,IGridNode b,IGridConnection connection){this.aDock=aDock;this.bDock=bDock;this.a=a;this.b=b;this.connection=connection;}
        public IGridConnection connection(){return connection;}
        public boolean valid(){return !destroyed&&pair(aDock,bDock)&&node(aDock,binding(aDock))==a&&node(bDock,binding(bDock))==b&&a.getConnections().contains(connection)&&b.getConnections().contains(connection);}
        public void destroy(){
            if(destroyed)return;destroyed=true;
            if(((AeDockAccess)aDock).ic$aeLink()==this)((AeDockAccess)aDock).ic$aeLink(null);
            if(((AeDockAccess)bDock).ic$aeLink()==this)((AeDockAccess)bDock).ic$aeLink(null);
            if(a.getConnections().contains(connection)||b.getConnections().contains(connection))connection.destroy();
        }
    }
}
