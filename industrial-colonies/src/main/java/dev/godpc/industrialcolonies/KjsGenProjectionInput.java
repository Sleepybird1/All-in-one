package dev.godpc.industrialcolonies;

import java.awt.event.KeyEvent;

/** Aspect-preserving projection geometry and desktop-to-GLFW key translation. */
public final class KjsGenProjectionInput {
    public record Viewport(double x,double y,double width,double height) {
        public double[] map(double px,double py,int guiWidth,int guiHeight,boolean clamp) {
            if(width<=0||height<=0||guiWidth<=0||guiHeight<=0)return null;
            double u=(px-x)/width,v=(py-y)/height;
            if(!clamp&&(u<0||v<0||u>=1||v>=1))return null;
            return new double[]{Math.max(0,Math.min(Math.nextDown((double)guiWidth),u*guiWidth)),Math.max(0,Math.min(Math.nextDown((double)guiHeight),v*guiHeight))};
        }
    }
    public static Viewport fit(int panelW,int panelH,int imageW,int imageH) {
        if(panelW<=0||panelH<=0||imageW<=0||imageH<=0)return new Viewport(0,0,0,0);
        double scale=Math.min((double)panelW/imageW,(double)panelH/imageH);
        double w=imageW*scale,h=imageH*scale;return new Viewport((panelW-w)/2,(panelH-h)/2,w,h);
    }
    public static int key(int awt,int location) {
        if(awt>=KeyEvent.VK_A&&awt<=KeyEvent.VK_Z||awt>=KeyEvent.VK_0&&awt<=KeyEvent.VK_9)return awt;
        if(awt>=KeyEvent.VK_F1&&awt<=KeyEvent.VK_F12)return 290+awt-KeyEvent.VK_F1;
        return switch(awt) {
            case KeyEvent.VK_ESCAPE->256;case KeyEvent.VK_ENTER->location==KeyEvent.KEY_LOCATION_NUMPAD?335:257;
            case KeyEvent.VK_TAB->258;case KeyEvent.VK_BACK_SPACE->259;case KeyEvent.VK_INSERT->260;case KeyEvent.VK_DELETE->261;
            case KeyEvent.VK_RIGHT->262;case KeyEvent.VK_LEFT->263;case KeyEvent.VK_DOWN->264;case KeyEvent.VK_UP->265;
            case KeyEvent.VK_PAGE_UP->266;case KeyEvent.VK_PAGE_DOWN->267;case KeyEvent.VK_HOME->268;case KeyEvent.VK_END->269;
            case KeyEvent.VK_SHIFT->location==KeyEvent.KEY_LOCATION_RIGHT?344:340;
            case KeyEvent.VK_CONTROL->location==KeyEvent.KEY_LOCATION_RIGHT?345:341;
            case KeyEvent.VK_ALT->location==KeyEvent.KEY_LOCATION_RIGHT?346:342;
            case KeyEvent.VK_META,KeyEvent.VK_WINDOWS->location==KeyEvent.KEY_LOCATION_RIGHT?347:343;
            case KeyEvent.VK_SPACE->32;case KeyEvent.VK_QUOTE->39;case KeyEvent.VK_COMMA->44;case KeyEvent.VK_MINUS->45;
            case KeyEvent.VK_PERIOD->46;case KeyEvent.VK_SLASH->47;case KeyEvent.VK_SEMICOLON->59;case KeyEvent.VK_EQUALS->61;
            case KeyEvent.VK_OPEN_BRACKET->91;case KeyEvent.VK_BACK_SLASH->92;case KeyEvent.VK_CLOSE_BRACKET->93;case KeyEvent.VK_BACK_QUOTE->96;
            default->-1;
        };
    }
}
