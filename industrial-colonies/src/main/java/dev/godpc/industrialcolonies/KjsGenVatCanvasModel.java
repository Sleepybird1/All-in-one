package dev.godpc.industrialcolonies;
import java.util.*;

/** Pure presentation of the existing TFMG machine list, with no recipe mutation. */
public final class KjsGenVatCanvasModel {
 public static final int EXTRA_INPUT_SLOTS = 20;
 public static final int EXTRA_INPUT_COLUMNS = 6;
 public static final int BOWL_CANVAS_HEIGHT = 176;
 public static final int BOWL_INPUT_X = 56;
 public static final int BOWL_INPUT_Y = 64;
 private KjsGenVatCanvasModel(){}
 public static int extraInputX(int origin,int index){return origin+(index%EXTRA_INPUT_COLUMNS)*18;}
 public static int extraInputY(int origin,int index){return origin+(index/EXTRA_INPUT_COLUMNS)*18;}
 public static int bowlInputX(int index){return extraInputX(BOWL_INPUT_X,index);}
 public static int bowlInputY(int index){return extraInputY(BOWL_INPUT_Y,index);}
 public static int bowlAttachmentX(int nativeX){return 2*(nativeX+12)-12;}
 public static boolean mayAppendExtraInput(int existing){return existing>=0&&existing<EXTRA_INPUT_SLOTS;}
 public static String namedVat(String id){
  return switch(id){
   case "industrial_colonies:tfmg_steel_vat_editor" -> "tfmg:steel_vat";
   case "industrial_colonies:tfmg_cast_iron_vat_editor" -> "tfmg:cast_iron_vat";
   case "industrial_colonies:tfmg_fireproof_vat_editor" -> "tfmg:firebrick_lined_vat";
   default -> null;
  };
 }
 public static String selectedMachines(String drive,String electrode,int count){
  if(count<0||count>3)throw new IllegalArgumentException("Choose zero to three electrodes");
  var result=new ArrayList<String>();
  switch(drive){case "None"->{} case "Mixer"->result.add("tfmg:mixing");case "Centrifuge"->result.add("tfmg:centrifuge");default->throw new IllegalArgumentException("Unknown vat drive");}
  String id=switch(electrode){case "Standard"->"tfmg:electrode";case "Graphite"->"tfmg:graphite_electrode";default->throw new IllegalArgumentException("Unknown electrode type");};
  for(int i=0;i<count;i++)result.add(id);
  if(result.size()>3)throw new IllegalArgumentException("The vat has three attachment positions; a mixer or centrifuge leaves room for two electrodes");
  return result.isEmpty()?"none":String.join(",",result);
 }
 public record Attachment(String id,int x,String label){}
 public static List<String> values(String serialized){
  if(serialized==null||serialized.isBlank())return List.of();
  return Arrays.stream(serialized.split(",")).map(String::trim).map(s->s.replace("'","").replace("\"","")).filter(s->!s.isBlank()).toList();
 }
 public static List<Attachment> attachments(String serialized){
  if("none".equals(serialized))return List.of();
  var ids=values(serialized);var result=new ArrayList<Attachment>();
  boolean center=ids.contains("tfmg:mixing")||ids.contains("tfmg:centrifuge");int electrode=0;
  for(String id:ids){
   String label=switch(id){case "tfmg:mixing"->"Mixer";case "tfmg:centrifuge"->"Centrifuge";case "tfmg:electrode"->"Electrode";case "tfmg:graphite_electrode"->"Graphite electrode";default->"Unknown attachment: "+id;};
   int x;
   if(id.equals("tfmg:mixing")||id.equals("tfmg:centrifuge"))x=43;
   else {int count=ids.size()-(center?1:0);x=count==1&&!center?43:(electrode==0?11:electrode==1&&count==3?43:75);electrode++;}
   result.add(new Attachment(id,x,label));
  }
  return List.copyOf(result);
 }
 public static String lining(String allowed){
  var types=values(allowed);return types.size()==1?types.getFirst():"any";
 }
}
