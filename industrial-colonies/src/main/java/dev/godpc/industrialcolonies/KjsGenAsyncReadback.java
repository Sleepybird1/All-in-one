package dev.godpc.industrialcolonies;
import org.lwjgl.opengl.*;
/** One asynchronous readback. Never waits for an unfinished GPU fence. Render-thread only. */
public final class KjsGenAsyncReadback implements AutoCloseable {
 private int buffer,size;private long fence;
 public void submit(int width,int height){
  if(fence!=0)throw new IllegalStateException("Readback already pending");
  int bytes=Math.multiplyExact(Math.multiplyExact(width,height),4);
  int previous=GL11.glGetInteger(GL21.GL_PIXEL_PACK_BUFFER_BINDING),alignment=GL11.glGetInteger(GL11.GL_PACK_ALIGNMENT);
  int row=GL11.glGetInteger(GL11.GL_PACK_ROW_LENGTH),skipRows=GL11.glGetInteger(GL11.GL_PACK_SKIP_ROWS),skipPixels=GL11.glGetInteger(GL11.GL_PACK_SKIP_PIXELS);
  try{
   if(buffer==0)buffer=GL15.glGenBuffers();GL15.glBindBuffer(GL21.GL_PIXEL_PACK_BUFFER,buffer);
   if(size!=bytes){GL15.glBufferData(GL21.GL_PIXEL_PACK_BUFFER,bytes,GL15.GL_STREAM_READ);size=bytes;}
   GL11.glPixelStorei(GL11.GL_PACK_ALIGNMENT,1);GL11.glPixelStorei(GL11.GL_PACK_ROW_LENGTH,0);GL11.glPixelStorei(GL11.GL_PACK_SKIP_ROWS,0);GL11.glPixelStorei(GL11.GL_PACK_SKIP_PIXELS,0);
   GL11.glReadPixels(0,0,width,height,GL12.GL_BGRA,GL11.GL_UNSIGNED_BYTE,0L);
   fence=GL32.glFenceSync(GL32.GL_SYNC_GPU_COMMANDS_COMPLETE,0);if(fence==0)throw new IllegalStateException("GPU fence creation failed");GL11.glFlush();
  }finally{GL15.glBindBuffer(GL21.GL_PIXEL_PACK_BUFFER,previous);GL11.glPixelStorei(GL11.GL_PACK_ALIGNMENT,alignment);GL11.glPixelStorei(GL11.GL_PACK_ROW_LENGTH,row);GL11.glPixelStorei(GL11.GL_PACK_SKIP_ROWS,skipRows);GL11.glPixelStorei(GL11.GL_PACK_SKIP_PIXELS,skipPixels);}
 }
 public byte[] poll(){
  if(fence==0)return null;
  int status=GL32.glClientWaitSync(fence,0,0);
  if(status==GL32.GL_TIMEOUT_EXPIRED)return null;
  if(status==GL32.GL_WAIT_FAILED)throw new IllegalStateException("GPU readback fence failed");
  int previous=GL11.glGetInteger(GL21.GL_PIXEL_PACK_BUFFER_BINDING);
  try{
   GL15.glBindBuffer(GL21.GL_PIXEL_PACK_BUFFER,buffer);
   var mapped=GL30.glMapBufferRange(GL21.GL_PIXEL_PACK_BUFFER,0,size,GL30.GL_MAP_READ_BIT);
   if(mapped==null)throw new IllegalStateException("GPU readback mapping failed");
   byte[] bytes=new byte[size];try{mapped.get(bytes);}finally{if(!GL15.glUnmapBuffer(GL21.GL_PIXEL_PACK_BUFFER))throw new IllegalStateException("GPU readback invalidated");}
   GL32.glDeleteSync(fence);fence=0;return bytes;
  }finally{GL15.glBindBuffer(GL21.GL_PIXEL_PACK_BUFFER,previous);}
 }
 @Override public void close(){if(fence!=0){GL32.glDeleteSync(fence);fence=0;}if(buffer!=0){GL15.glDeleteBuffers(buffer);buffer=0;size=0;}}
}
