#pragma once

#include "ofMain.h"
#include "ofxOpenCv.h"
#include "ofxCv.h"
#include "ofxXmlSettings.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);
	
    
    
    
		ofImage	dilbertOfImageRaw;
        ofImage dilbertOfImageBlob;
		ofxCvColorImage dilbertCvColorImage;
		ofxCvGrayscaleImage dilbertCvGrayImage;
		ofxCvGrayscaleImage dilbertCvGrayImage2;
		IplImage* dilbertColorIplImage;
	
		ofxCvColorImage dilbertFloodFilledColorImage;
	int blackFloodfillThreshold;
	int bgFloodFillThreshold;
	int findTextThreshold;
    int numPanels = 3;
	
	ofxCvContourFinder 	contourFinder;
	
	int dilbertW;
	int dilbertH;
    
    ofxXmlSettings XML;
    int lastTagNumber;
	
	
	
	
};
