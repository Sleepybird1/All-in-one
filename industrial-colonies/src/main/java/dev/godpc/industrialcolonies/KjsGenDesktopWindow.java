package dev.godpc.industrialcolonies;

import javax.swing.*;
import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.charset.StandardCharsets;

/** A projection surface, not a second recipe editor. All widgets run in Minecraft. */
public final class KjsGenDesktopWindow {
    private final JFrame frame=new JFrame("KubeJS Gen — projected game editor");
    private final Surface surface=new Surface();
    private final PrintWriter out=new PrintWriter(new OutputStreamWriter(System.out,StandardCharsets.UTF_8),true);
    private BufferedImage image;
    private int guiWidth,guiHeight,epoch;
    private double lastX,lastY;
    private int held=-1;
    private void send(String... values){out.println(KjsGenDesktopProtocol.encode(values));}
    private void event(String action,String... args){String[] values=new String[args.length+2];values[0]=action;values[1]=Integer.toString(epoch);System.arraycopy(args,0,values,2,args.length);send(values);}
    private int modifiers(InputEvent e){return (e.isShiftDown()?1:0)|(e.isControlDown()?2:0)|(e.isAltDown()?4:0)|(e.isMetaDown()?8:0);}
    private double[] point(MouseEvent e,boolean clamp){return image==null?null:KjsGenProjectionInput.fit(surface.getWidth(),surface.getHeight(),image.getWidth(),image.getHeight()).map(e.getX(),e.getY(),guiWidth,guiHeight,clamp);}
    private void build(){
        surface.setFocusable(true);surface.setFocusTraversalKeysEnabled(false);surface.setBackground(Color.BLACK);
        var mouse=new MouseInput();surface.addMouseListener(mouse);surface.addMouseMotionListener(mouse);surface.addMouseWheelListener(mouse);surface.addKeyListener(new KeyboardInput());
        surface.addComponentListener(new ResizeHandler());
        frame.addWindowListener(new Lifecycle());frame.addWindowFocusListener(new Lifecycle());frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
        frame.setContentPane(surface);frame.setMinimumSize(new Dimension(640,400));frame.setSize(1280,800);frame.setLocationRelativeTo(null);frame.setVisible(true);surface.requestFocusInWindow();
    }
    private final class Surface extends JPanel {
        @Override protected void paintComponent(Graphics g){super.paintComponent(g);if(image==null){g.setColor(Color.WHITE);g.drawString("Waiting for the KubeJS Gen interface...",24,36);return;}
            var v=KjsGenProjectionInput.fit(getWidth(),getHeight(),image.getWidth(),image.getHeight());
            ((Graphics2D)g).setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BILINEAR);
            g.drawImage(image,(int)v.x(),(int)v.y(),(int)v.width(),(int)v.height(),null);
        }
    }
    private final class MouseInput extends MouseAdapter {
        @Override public void mousePressed(MouseEvent e){var p=point(e,false);if(p==null)return;surface.requestFocusInWindow();held=e.getButton()==MouseEvent.BUTTON1?0:e.getButton()==MouseEvent.BUTTON3?1:2;lastX=p[0];lastY=p[1];event("DOWN",Double.toString(p[0]),Double.toString(p[1]),Integer.toString(held),Integer.toString(modifiers(e)));}
        @Override public void mouseReleased(MouseEvent e){var p=point(e,true);if(p==null||held<0)return;event("UP",Double.toString(p[0]),Double.toString(p[1]),Integer.toString(held),Integer.toString(modifiers(e)));held=-1;}
        @Override public void mouseMoved(MouseEvent e){var p=point(e,false);if(p!=null)event("MOVE",Double.toString(p[0]),Double.toString(p[1]),Integer.toString(modifiers(e)));}
        @Override public void mouseDragged(MouseEvent e){var p=point(e,true);if(p==null||held<0)return;event("DRAG",Double.toString(p[0]),Double.toString(p[1]),Integer.toString(held),Double.toString(p[0]-lastX),Double.toString(p[1]-lastY),Integer.toString(modifiers(e)));lastX=p[0];lastY=p[1];}
        @Override public void mouseWheelMoved(MouseWheelEvent e){var p=point(e,false);if(p!=null)event("SCROLL",Double.toString(p[0]),Double.toString(p[1]),Double.toString(-e.getPreciseWheelRotation()),Integer.toString(modifiers(e)));}
    }
    private final class KeyboardInput extends KeyAdapter {
        @Override public void keyPressed(KeyEvent e){int key=KjsGenProjectionInput.key(e.getKeyCode(),e.getKeyLocation());if(key>=0)event("KEY",Integer.toString(key),"1",Integer.toString(modifiers(e)));e.consume();}
        @Override public void keyReleased(KeyEvent e){int key=KjsGenProjectionInput.key(e.getKeyCode(),e.getKeyLocation());if(key>=0)event("KEY",Integer.toString(key),"0",Integer.toString(modifiers(e)));e.consume();}
        @Override public void keyTyped(KeyEvent e){if(!Character.isISOControl(e.getKeyChar())&&e.getKeyChar()!=KeyEvent.CHAR_UNDEFINED)event("CHAR",Integer.toString(e.getKeyChar()),Integer.toString(modifiers(e)));e.consume();}
    }
    private final class ResizeHandler extends ComponentAdapter {
        private final Timer debounce=new Timer(180,e->send("RESIZE",Integer.toString(surface.getWidth()),Integer.toString(surface.getHeight())));
        {debounce.setRepeats(false);}
        @Override public void componentResized(ComponentEvent e){debounce.restart();}
    }
    private final class Lifecycle extends WindowAdapter {
        @Override public void windowClosing(WindowEvent e){send("CLOSE");frame.dispose();System.exit(0);}
        @Override public void windowGainedFocus(WindowEvent e){event("FOCUS","1");surface.requestFocusInWindow();}
        @Override public void windowLostFocus(WindowEvent e){event("FOCUS","0");held=-1;}
    }
    private void accept(BufferedImage next,int w,int h,int screenEpoch){image=next;guiWidth=w;guiHeight=h;epoch=screenEpoch;surface.repaint();event("ACK");}
    public static void main(String[] args)throws Exception {
        UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        var holder=new KjsGenDesktopWindow[1];SwingUtilities.invokeAndWait(()->{holder[0]=new KjsGenDesktopWindow();holder[0].build();});var ui=holder[0];
        try(var in=new DataInputStream(new BufferedInputStream(System.in))){
            while(true){int format=in.readInt();if(format!=0x49435031&&format!=0x49435231)throw new IOException("Invalid editor frame");int epoch=in.readInt(),w=in.readInt(),h=in.readInt(),length=in.readInt();if(w<1||h<1||length<1||length>32*1024*1024)throw new IOException("Invalid frame size");byte[] bytes=in.readNBytes(length);if(bytes.length!=length)throw new EOFException();var image=format==0x49435231?KjsGenFramePixels.decode(bytes):ImageIO.read(new ByteArrayInputStream(bytes));if(image==null)throw new IOException("Invalid frame image");SwingUtilities.invokeAndWait(()->ui.accept(image,w,h,epoch));}
        }catch(EOFException expected){}finally{System.exit(0);}
    }
}
