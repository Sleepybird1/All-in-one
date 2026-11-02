package dev.godpc.industrialcolonies;
import java.awt.image.*;
import java.nio.*;
public final class KjsGenFramePixels {
 public static BufferedImage decode(byte[] payload){
  var header=ByteBuffer.wrap(payload);int w=header.getInt(),h=header.getInt();
  if(w<1||w>1920||h<1||h>1200||payload.length!=8+(long)w*h*4)throw new IllegalArgumentException("Invalid raw frame");
  var image=new BufferedImage(w,h,BufferedImage.TYPE_INT_ARGB);int[] pixels=((DataBufferInt)image.getRaster().getDataBuffer()).getData();
  var source=header.slice().order(ByteOrder.LITTLE_ENDIAN).asIntBuffer();
  for(int y=0;y<h;y++)source.get(pixels,(h-1-y)*w,w);
  return image;
 }
}
