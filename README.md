# Bensky Image Editor

BIE is an simple an editor for simple and common image adjustments such as contrast, saturation, brightness etc. The project is still in progress.

![image](https://user-images.githubusercontent.com/84646869/181303733-c8bdd2cd-9af2-463f-9df1-9f80bef6525e.png)

![image](https://user-images.githubusercontent.com/84646869/181299206-47ad6106-4518-4732-9cc7-72daea2fcf7f.png)

# Process

The adjustment features were implemented using Numpy, Python's scientific computing library.

I goal was to implement those features from scratch, without using an off the shelf image editing library. Although I did use an image library to convert the images to an array of pixels so they could be manipulated with Numpy, I was able to accomplish that goal. But that did come at the great cost of speed, due to Python's slow execution. Those off the shelf libraries are often implemented in C/C++.  
