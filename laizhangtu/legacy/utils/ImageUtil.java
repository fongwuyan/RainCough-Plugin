import java.io.*;

import android.graphics.*;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.content.Context;
import android.renderscript.Allocation;
import android.renderscript.Element;
import android.renderscript.RenderScript;
import android.renderscript.ScriptIntrinsicBlur;

public class ImageUtil {

    public static Bitmap flipImage(Bitmap originalBitmap) {
	    Matrix matrix = new Matrix();
        matrix.setScale(-1, 1);

        Bitmap flippedBitmap = Bitmap.createBitmap(originalBitmap, 0, 0,
            originalBitmap.getWidth(), originalBitmap.getHeight(), matrix, true);
            
        return flippedBitmap;
	}
	
	public static Bitmap mflipImage(Bitmap originalBitmap) {
	    Matrix matrix = new Matrix();
        matrix.setScale(1, -1);

        Bitmap flippedBitmap = Bitmap.createBitmap(originalBitmap, 0, 0,
            originalBitmap.getWidth(), originalBitmap.getHeight(), matrix, true);
            
        return flippedBitmap;
	}
    
    
    public static Bitmap blurImage(Bitmap bitmap) {
		return blurImg(bitmap, 15f);
	} 
   
    private static Bitmap blurImg(Bitmap bitmap, float radius) {
        if (radius < 0) {
            throw new IllegalArgumentException("Radius must be >= 0");
        }
        if (radius > 25) {
            radius = 25;
        }

        // Create a RenderScript context
        RenderScript rs = RenderScript.create(context);

        // Create an allocation from the bitmap to use with the blur
        Allocation input = Allocation.createFromBitmap(rs, bitmap);
        Allocation output = Allocation.createTyped(rs, input.getType());

        // Create the intrinsic blur script using the RenderScript context
        ScriptIntrinsicBlur blurScript = ScriptIntrinsicBlur.create(rs, Element.U8_4(rs));
        blurScript.setRadius(radius); // Set the radius of the blur
        blurScript.setInput(input);   // Set the input allocation
        blurScript.forEach(output);   // Apply the blur

        // Copy the output to the blurred bitmap
        Bitmap blurredBitmap = Bitmap.createBitmap(bitmap.getWidth(), bitmap.getHeight(), bitmap.getConfig());
        output.copyTo(blurredBitmap);

        // Destroy the RenderScript context and allocations to release memory
        rs.destroy();
        input.destroy();
        output.destroy();
        blurScript.destroy();

        return blurredBitmap;
    }

    
    public static void outImage(Bitmap outBitmap, String imagePath) {
        File imageFile = new File(imagePath);
        FileOutputStream outputStream = new FileOutputStream(imageFile);
        outBitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream);
        outputStream.flush();
        outputStream.close();

        outBitmap.recycle();
	        
    }
    
}
