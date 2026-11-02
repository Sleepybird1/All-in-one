package dev.godpc.industrialcolonies.geology;
import java.util.*;
import net.minecraft.util.StringRepresentable;
/** Visual identity only; rich content and extraction reserves remain in the owner ledger. */
public enum NodeAppearance implements StringRepresentable {
    GENERIC, SPHALERITE, CHALCOPYRITE, HEMATITE, MAGNETITE, BAUXITE, SPODUMENE_ROCK, ARGENTITE, WOLFRAMITE_ROCK, PENTLANDITE, GALENA, DOLOMITE, GRAPHITE_ROCK, PHOSPHATE_ROCK, COAL, DIAMOND, COBALT, URANIUM, THORIUM, ULTRAMAFIC_ROCK, OSMIUM, IRIDIUM, PLATINUM, ILMENITE, BERTRANDITE, BORAX_ROCK, CASSITERITE, CHROMITE, VIBRANIUM, QUARTZ, ANCIENT_DEBRIS, GOLD;
    private final String serialized=name().toLowerCase(Locale.ROOT);
    private static final Map<String,NodeAppearance> BY_FAMILY=Arrays.stream(values()).collect(java.util.stream.Collectors.toUnmodifiableMap(NodeAppearance::getSerializedName,value->value));
    @Override public String getSerializedName(){return serialized;}
    public static NodeAppearance forFamily(String family){
        if("veridium".equals(family))return VIBRANIUM;
        return family==null?GENERIC:BY_FAMILY.getOrDefault(family,GENERIC);
    }
}
