#include "ofApp.h"
#include "time.h"

//--------------------------------------------------------------
void ofApp::setup(){
	
    int currentDay = ofGetDay();
    int currentYear = ofGetYear();
    int currentMonth = ofGetMonth();
    
    time_t rawtime;
    time ( &rawtime );
//    printf ( "The current local time is: %s", ctime (&rawtime) );
//    printf ( "The current month is %d\n", currentMonth);
//    printf ( "The current day is %d\n", currentDay);
//    printf ( "The current year is %d\n", currentYear);
    
    time_t tim=time(NULL);
    tm *now=localtime(&tim);
    printf("Today is %d/%02d/%02d\n", now->tm_year+1900, now->tm_mon+1, now->tm_mday);
//    now->tm_mday -= 109;
    now->tm_mday -= 57;
    mktime(now);
    printf("Date is now %d/%02d/%02d\n", now->tm_year+1900, now->tm_mon+1, now->tm_mday);
    
    XML.clear();
    XML.addTag("DATA");
    XML.pushTag("DATA");
    
    int strip_in_xml = -1;
    
    for (int day=0; day<9510; day++) {
        now->tm_mday -=1;
        mktime(now);
        
        char strip_date[15];
        int strip_year = now->tm_year+1900;
        int strip_month = now->tm_mon+1;
        int strip_day = now->tm_mday;
        
        sprintf(strip_date, "%d-%02d-%02d", strip_year,strip_month,strip_day);
        printf("The date is %s\n",strip_date);
        string a_panel = "a";
        string b_panel = "b";
        string c_panel = "c";
        string image_type = ".gif";
        string path = "../../../../../../homework12/dilbert_stuff/individual_strips/";
        string strip_date_a_panel = strip_date + a_panel + image_type;
        string strip_date_b_panel = strip_date + b_panel + image_type;
        string strip_date_c_panel = strip_date + c_panel + image_type;
        string panel_to_process;
        string panel_only;
        
        string panel_without_path;
        
//        XML.clear();
//        XML.addTag("DATA");
//        XML.pushTag("DATA");
        
        for (int which_panel=0; which_panel<numPanels; which_panel++) {
            
            switch (which_panel) {
                case 0:
                    panel_to_process = path + strip_date + a_panel + image_type;
                    panel_without_path = strip_date + a_panel + image_type;
                    panel_only = strip_date + a_panel;
                    break;
                case 1:
                    panel_to_process = path + strip_date + b_panel + image_type;
                    panel_without_path = strip_date + b_panel + image_type;
                    panel_only = strip_date + b_panel;
                    break;
                case 2:
                    panel_to_process = path + strip_date + c_panel + image_type;
                    panel_without_path = strip_date + c_panel + image_type;
                    panel_only = strip_date + c_panel;
                    break;
            }
            
            //	dilbertOfImageRaw.loadImage ("dilbert2.gif");
            //    dilbertOfImageRaw.loadImage ("2015-01-02b.gif");
            if (ofFile::doesFileExist(panel_to_process)) {
                
                strip_in_xml++;
                printf("Strip tracker is %i\n",strip_in_xml);
                
                dilbertOfImageRaw.loadImage(panel_to_process);
                bool ImageLoaded = dilbertOfImageRaw.loadImage(panel_to_process);
//                printf("ImageLoaded is %i\n", ImageLoaded);
                
                printf("Processing panel %s\n",panel_to_process.c_str());
                
                dilbertW = dilbertOfImageRaw.getWidth();
//                printf("Iteration %i, Width %i\n",which_panel,dilbertW);
                dilbertH = dilbertOfImageRaw.getHeight();
                dilbertFloodFilledColorImage.allocate(dilbertW, dilbertH);
                
                XML.addTag("STRIP");
                
                findTextThreshold = 140;
                
                unsigned char *dilbertOfImageRawPixels = dilbertOfImageRaw.getPixels();
                dilbertCvColorImage.setFromPixels (dilbertOfImageRawPixels, dilbertW, dilbertH);
                dilbertColorIplImage = dilbertCvColorImage.getCvImage();
                
                
                // Flood fill from the black upper-left corner; this will kill the characters that are touching the bottom edge.
                // Because the characters are ALWAYS TOUCHING THE BOTTOM EDGE. Because.
                blackFloodfillThreshold = 130;
                CvPoint blackSeedPoint = cvPoint(1,1);
                int floodFlags1 = 8 | cv::FLOODFILL_FIXED_RANGE;
                cvFloodFill (dilbertColorIplImage, blackSeedPoint, CV_RGB(255,255,255),
                             CV_RGB(blackFloodfillThreshold,blackFloodfillThreshold,blackFloodfillThreshold),
                             CV_RGB(blackFloodfillThreshold,blackFloodfillThreshold,blackFloodfillThreshold),
                             NULL,floodFlags1,NULL);
                
                // Flood fill to clobber the gradient;
                CvPoint backgroundSeedPoint = cvPoint(8,8);
                int floodFlags2 = 8 | cv::FLOODFILL_FIXED_RANGE;
                bgFloodFillThreshold = 70;
                cvFloodFill (dilbertColorIplImage, backgroundSeedPoint, CV_RGB(255,255,255),
                             CV_RGB(bgFloodFillThreshold,bgFloodFillThreshold,bgFloodFillThreshold),
                             CV_RGB(bgFloodFillThreshold,bgFloodFillThreshold,bgFloodFillThreshold),
                             NULL,floodFlags2,NULL);
                
                
                // Convert to grayscale and threshold; this isolates the (remaining) black stuff,
                // which is (we hope) the letters.
                dilbertCvGrayImage.clear();
                dilbertCvGrayImage = dilbertCvColorImage;
                dilbertCvGrayImage.threshold( findTextThreshold );
                dilbertCvGrayImage.invert();
                
                // Take a lovely median filter. This gets rid of single-pixel salt noise.
                cv::Mat srcMat = ofxCv::toCv (dilbertCvGrayImage);
                cv::medianBlur(srcMat, srcMat, 5);
                
                // Get the median-filtered data back into the dilbertCvGrayImage,
                // because the above was done on a copy by value (not reference)
                ofPixels somePixels;
                ofxCv::toOf(srcMat, somePixels);
                dilbertCvGrayImage.setFromPixels(somePixels);
                
                // Dilate the letters and letter-fragments to consolidate them into a single blob per phrase.
                int nTimesToDilate = 7;
                for (int i=0; i<nTimesToDilate; i++){
                    dilbertCvGrayImage.dilate_3x3();
                }
                
                // find contours.
                // also, find holes is set to true so we will get interior contours as well....
                int minBlobArea = 25*25;
                int maxBlobArea = dilbertW * dilbertH /2;
                int maxNumberOfBlobsRequested = 3;
                contourFinder.findContours(dilbertCvGrayImage, minBlobArea, maxBlobArea, maxNumberOfBlobsRequested, false);
                
                vector<ofxCvBlob> theBlobs = contourFinder.blobs;
                vector<ofxCvBlob> theOrderedBlobs = contourFinder.blobs;
                
                
//                XML.addAttribute("STRIP", "FILENAME", panel_without_path,which_panel);
//                XML.setAttribute("STRIP", "FILENAME", panel_without_path,which_panel);
                XML.addAttribute("STRIP", "FILENAME", panel_without_path,strip_in_xml);
                XML.setAttribute("STRIP", "FILENAME", panel_without_path,strip_in_xml);
//                XML.pushTag("STRIP", which_panel);
                printf("************************Strip number %i********************************\n",strip_in_xml);
                XML.pushTag("STRIP", strip_in_xml);
                
                int nDiscoveredBlobs = contourFinder.nBlobs;
                
                // Order the Blobs by x-coordinate (smallest to largest) since OCR reads XML file from top to bottom
                if (nDiscoveredBlobs > 1) {
//                    printf("Blob0-x %f Blob1-x %f\n", theBlobs[0].boundingRect.x,theBlobs[1].boundingRect.x);
                    if ((theBlobs[0].boundingRect.x) > (theBlobs[1].boundingRect.x))
                        swap(theBlobs[0], theBlobs[1]);
                }
                if (nDiscoveredBlobs > 2) {
//                    printf("Blob1-x %f Blob2-x %f\n", theBlobs[0].boundingRect.x,theBlobs[2].boundingRect.x);
                    if ((theBlobs[0].boundingRect.x) > (theBlobs[2].boundingRect.x))
                        swap(theBlobs[0], theBlobs[2]);
                    if ((theBlobs[1].boundingRect.x) > (theBlobs[2].boundingRect.x))
                        swap(theBlobs[1], theBlobs[2]);
                }
                
                for (int i=0; i<nDiscoveredBlobs; i++){
                    ofxCvBlob ithBlob = theBlobs[i];
                    dilbertOfImageBlob = dilbertOfImageRaw;
                    
                    ofRectangle boundingRect = ithBlob.boundingRect;
                    float x = boundingRect.x;
                    float y = boundingRect.y;
                    float w = boundingRect.width;
                    float h = boundingRect.height;
                    //
                    //            XML.addAttribute("STRIP", "FILENAME", panel_to_process,0);
                    //            XML.setAttribute("STRIP", "FILENAME", panel_to_process,0);
                    //            XML.pushTag("STRIP");
                    
                    XML.addTag("CROP_REGION");
                    XML.pushTag("CROP_REGION",i);
                    XML.addValue("X", x);
                    XML.addValue("Y", y);
                    XML.addValue("W", w);
                    XML.addValue("H", h);
                    XML.popTag(); // CROP_REGION
                    
                    dilbertOfImageBlob.crop(x, y, w, h);
//                    dilbertOfImageBlob.saveImage("Blob"+ofToString(i)+"-"+ofToString(panel_to_process));
                    dilbertOfImageBlob.saveImage(ofToString(panel_only)+"-"+"Blob"+ofToString(i)+ofToString(image_type));
                    printf("%d: %f	%f	%f	%f\n", i, x,y,w,h);
                } //for (int i=0; i<nDiscoveredBlobs; i++)
                XML.popTag(); //STRIP
                //        XML.popTag();
                printf ("---------------------\n");
            } else {
                printf("File %s does not exist\n", panel_to_process.c_str());
            }
            
        } //for (int i=0; i<numPanels; i++)
        //XML.popTag();
    } //for (int day=0; day<9600; day++)
    XML.popTag();
    XML.saveFile("../roncrop.xml");
    
}

//--------------------------------------------------------------
void ofApp::update(){
	
	
//	unsigned char *dilbertOfImageRawPixels = dilbertOfImageRaw.getPixels();
//	dilbertCvColorImage.setFromPixels (dilbertOfImageRawPixels, dilbertW, dilbertH);
//	dilbertColorIplImage = dilbertCvColorImage.getCvImage();
//	
//	
//	// Flood fill from the black upper-left corner; this will kill the characters that are touching the bottom edge.
//	// Because the characters are ALWAYS TOUCHING THE BOTTOM EDGE. Because.
//	blackFloodfillThreshold = 130;
//	CvPoint blackSeedPoint = cvPoint(1,1);
//	int floodFlags1 = 8 | cv::FLOODFILL_FIXED_RANGE;
//	cvFloodFill (dilbertColorIplImage, blackSeedPoint, CV_RGB(255,255,255),
//				 CV_RGB(blackFloodfillThreshold,blackFloodfillThreshold,blackFloodfillThreshold),
//				 CV_RGB(blackFloodfillThreshold,blackFloodfillThreshold,blackFloodfillThreshold),
//				 NULL,floodFlags1,NULL);
//	
//	// Flood fill to clobber the gradient;
//	CvPoint backgroundSeedPoint = cvPoint(8,8);
//	int floodFlags2 = 8 | cv::FLOODFILL_FIXED_RANGE;
//	bgFloodFillThreshold = 70;
//	cvFloodFill (dilbertColorIplImage, backgroundSeedPoint, CV_RGB(255,255,255),
//				 CV_RGB(bgFloodFillThreshold,bgFloodFillThreshold,bgFloodFillThreshold),
//				 CV_RGB(bgFloodFillThreshold,bgFloodFillThreshold,bgFloodFillThreshold),
//				 NULL,floodFlags2,NULL);
//
//	
//	// Convert to grayscale and threshold; this isolates the (remaining) black stuff,
//	// which is (we hope) the letters.
//	dilbertCvGrayImage = dilbertCvColorImage;
//	dilbertCvGrayImage.threshold( findTextThreshold );
//	dilbertCvGrayImage.invert();
//	
//
//	// Take a lovely median filter. This gets rid of single-pixel salt noise.
//	cv::Mat srcMat = ofxCv::toCv (dilbertCvGrayImage);
//	cv::medianBlur(srcMat, srcMat, 5);
//
//	// Get the median-filtered data back into the dilbertCvGrayImage,
//	// because the above was done on a copy by value (not reference)
//	ofPixels somePixels;
//	ofxCv::toOf(srcMat, somePixels);
//	dilbertCvGrayImage.setFromPixels(somePixels);
//	
//	// Dilate the letters and letter-fragments to consolidate them into a single blob per phrase.
//	int nTimesToDilate = 7;
//	for (int i=0; i<nTimesToDilate; i++){
//		dilbertCvGrayImage.dilate_3x3();
//	}
//	
//	// find contours.
//	// also, find holes is set to true so we will get interior contours as well....
//	int minBlobArea = 25*25;
//	int maxBlobArea = dilbertW * dilbertH /2;
//	int maxNumberOfBlobsRequested = 3;
//	contourFinder.findContours(dilbertCvGrayImage, minBlobArea, maxBlobArea, maxNumberOfBlobsRequested, false);
//	
//    dilbertOfImageBlob = dilbertOfImageRaw;
//    
//	vector<ofxCvBlob> theBlobs = contourFinder.blobs;
//	int nDiscoveredBlobs = contourFinder.nBlobs;
//	for (int i=0; i<nDiscoveredBlobs; i++){
//		ofxCvBlob ithBlob = theBlobs[i];
//		ofRectangle boundingRect = ithBlob.boundingRect;
//		float x = boundingRect.x;
//		float y = boundingRect.y;
//		float w = boundingRect.width;
//		float h = boundingRect.height;
//        dilbertOfImageBlob.crop(x, y, w, h);
//        dilbertOfImageBlob.saveImage("Blob"+ofToString(i)+".gif");
//
//
////        ithBlob.saveImage("Blob"+ofToString(i)+".png");
//		printf("%d: %f	%f	%f	%f\n", i, x,y,w,h);
//	}
//	printf ("---------------------\n");

}

//--------------------------------------------------------------
void ofApp::draw(){
	
	int margin = 10;
	
	dilbertOfImageRaw.draw	(margin*1,				margin);
	dilbertCvColorImage.draw(margin*2 + dilbertW*1,	margin);
	dilbertCvGrayImage.draw	(margin*3 + dilbertW*2,	margin);
	
	contourFinder.draw		(margin*3 + dilbertW*2,	margin);
	

	int mx = max (1, 1 + (mouseX % 255));
	ofSetColor (255);
	ofDrawBitmapString( ofToString (mx),margin*2 + dilbertW, dilbertH + 50);

}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){ 

}
