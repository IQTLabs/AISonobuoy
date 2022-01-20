/* Edge Impulse Arduino examples
 * Copyright (c) 2021 EdgeImpulse Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

// If your target is limited in memory remove this macro to save 10K RAM
#define EIDSP_QUANTIZE_FILTERBANK   0
#define USE_EXTERNAL_MIC A1
//#define AUDIO_OUT A0     
/* Includes ---------------------------------------------------------------- */

#include <boat-detector_inferencing.h>
#include <Adafruit_Arcada.h>
#include <CircularBuffer.h>
#include <Math.h>

// Color definitions
#define BACKGROUND_COLOR __builtin_bswap16(ARCADA_BLACK)
#define BORDER_COLOR __builtin_bswap16(ARCADA_BLUE)
#define PLOT_COLOR_1 __builtin_bswap16(ARCADA_YELLOW)
#define TITLE_COLOR __builtin_bswap16(ARCADA_WHITE)
#define TICKTEXT_COLOR __builtin_bswap16(ARCADA_WHITE)
#define TICKLINE_COLOR __builtin_bswap16(ARCADA_DARKGREY)

// Buffers surrounding the plot area
#define PLOT_TOPBUFFER 20
#define PLOT_LEFTBUFFER 40
#define PLOT_BOTTOMBUFFER 20
#define PLOT_W (ARCADA_TFT_WIDTH - PLOT_LEFTBUFFER)
#define PLOT_H (ARCADA_TFT_HEIGHT - PLOT_BOTTOMBUFFER - PLOT_TOPBUFFER)

// Which pin to plot
#define ANALOG_INPUT A1

// Buffer for our plot data
CircularBuffer<float, PLOT_W> data_buffer;

/** Audio buffers, pointers and selectors */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static signed short sampleBuffer[2048];
static bool debug_nn = false; // Set this to true to see e.g. features generated from the raw signal
static char graph_title[100];


Adafruit_Arcada arcada;


/**
 * @brief      Arduino setup function
 */
void setup()
{
    // put your setup code here, to run once:
    Serial.begin(115200);

    Serial.println("Edge Impulse Inferencing Demo");

    // summary of inferencing settings (from model_metadata.h)
    ei_printf("Inferencing settings:\n");
    ei_printf("\tInterval: %.2f ms.\n", (float)EI_CLASSIFIER_INTERVAL_MS);
    ei_printf("\tFrame size: %d\n", EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);
    ei_printf("\tSample length: %d ms.\n", EI_CLASSIFIER_RAW_SAMPLE_COUNT / 16);
    ei_printf("\tNo. of classes: %d\n", sizeof(ei_classifier_inferencing_categories) / sizeof(ei_classifier_inferencing_categories[0]));

    if (microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT) == false) {
        ei_printf("ERR: Failed to setup audio sampling\r\n");
        return;
    }
      // Hook up the callback that will be called with each sample
  #if defined(USE_EXTERNAL_MIC)
    arcada.timerCallback(EI_CLASSIFIER_FREQUENCY, TIMER_CALLBACK);
    analogReadResolution(12);
  #endif
  #if defined(AUDIO_OUT) 
  pinMode(AUDIO_OUT, OUTPUT);
  analogWriteResolution(12);
#endif
  // Start TFT and fill black
  if (!arcada.arcadaBegin()) {
    Serial.print("Failed to begin");
    while (1) delay(10);
  }
  arcada.displayBegin();
  
  // Turn on backlight
  arcada.setBacklight(255); 
  if (! arcada.createFrameBuffer(ARCADA_TFT_WIDTH, ARCADA_TFT_HEIGHT)) {
    Serial.print("Failed to allocate framebuffer");
    while (1);
  }
}



uint32_t timestamp = 0;
/**
 * @brief      Arduino main function. Runs the inferencing loop.
 */
void loop()
{
    ei_printf("Starting inferencing in 2 seconds...\n");

    delay(2000);

    ei_printf("Recording...\n");

    bool m = microphone_inference_record();
    if (!m) {
        ei_printf("ERR: Failed to record audio...\n");
        return;
    }

    ei_printf("Recording done\n");

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;
    ei_impulse_result_t result = { 0 };

    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", r);
        return;
    }

    // print the predictions
    ei_printf("Predictions ");
    ei_printf("(DSP: %d ms., Classification: %d ms., Anomaly: %d ms.)",
        result.timing.dsp, result.timing.classification, result.timing.anomaly);
    ei_printf(": \n");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        ei_printf("    %s: %.5f\n", result.classification[ix].label, result.classification[ix].value);
    }

    if (result.classification[0].value > result.classification[1].value) {
      sprintf(graph_title, "Boat %.2f", result.classification[0].value);
      arcada.pixels.fill(arcada.pixels.Color(0, 50, 0));
      arcada.pixels.show();
    } else {
      sprintf(graph_title, "No Boat %.2f", result.classification[1].value);
      arcada.pixels.fill(arcada.pixels.Color(50, 0, 0));
      arcada.pixels.show();
    }
    
  plotBuffer(arcada.getCanvas(), inference.buffer, inference.n_samples, graph_title);
  arcada.blitFrameBuffer(0, 0, false, true);


}




void plotBuffer(GFXcanvas16 *_canvas, int16_t *buffer, uint32_t buf_len, char *title) {
  _canvas->fillScreen(BACKGROUND_COLOR);
  _canvas->drawLine(PLOT_LEFTBUFFER-1, PLOT_TOPBUFFER, 
                    PLOT_LEFTBUFFER-1, PLOT_H+PLOT_TOPBUFFER, BORDER_COLOR);
  _canvas->drawLine(PLOT_LEFTBUFFER-1, PLOT_TOPBUFFER+PLOT_H+1, 
                    ARCADA_TFT_WIDTH, PLOT_TOPBUFFER+PLOT_H+1, BORDER_COLOR);
  _canvas->setTextSize(2);
  _canvas->setTextColor(TITLE_COLOR);
  uint16_t title_len = strlen(title) * 12;
  _canvas->setCursor((_canvas->width()-title_len)/2, 0);
  _canvas->print(title);
  
  float minY = 0;
  float maxY = 0;

 
  maxY = minY = buffer[0];
  
  for (int i=0; i< buf_len; i++) {
    minY = min(minY, buffer[i]);
    maxY = max(maxY, buffer[i]);
  }
  //Serial.printf("Data range: %f ~ %f\n", minY, maxY);

  float MIN_DELTA = 10.0;
  if (maxY - minY < MIN_DELTA) {
     float mid = (maxY + minY) / 2;
     maxY = mid + MIN_DELTA / 2;
     minY = mid - MIN_DELTA / 2;
  } else {
    float extra = (maxY - minY) / 10;
    maxY += extra;
    minY -= extra;
  }
  //Serial.printf("Y range: %f ~ %f\n", minY, maxY);

  printTicks(_canvas, 5, minY, maxY);

  int16_t last_y = 0, last_x = 0;
  uint32_t buf_step = 0;
  int16_t steps = floor(buf_len / PLOT_W);
  for (int i=0; i<PLOT_W; i++) {

    int16_t y = map(buffer[buf_step], minY, maxY, PLOT_TOPBUFFER+PLOT_H, PLOT_TOPBUFFER);
        buf_step = buf_step + steps;
    //Serial.printf("%0.1f -> %d, ", cbuffer[i], y);
    int16_t x = PLOT_LEFTBUFFER+i;
    //y = TFT_H - y + PLOT_BOTTOMBUFFER - PLOT_TOPBUFFER;
    if (i == 0) {
      last_y = y;
      last_x = x;
    }
    _canvas->drawLine(last_x, last_y, x, y, PLOT_COLOR_1);
    last_x = x;
    last_y = y;
  }

}


void printTicks(GFXcanvas16 *_canvas, uint8_t ticks, float minY, float maxY) {
  _canvas->setTextSize(1);
  _canvas->setTextColor(TICKTEXT_COLOR);
  // Draw ticks
  for (int t=0; t<ticks; t++) {
    float v = map(t, 0, ticks-1, minY, maxY);
    uint16_t y = map(t, 0, ticks-1, ARCADA_TFT_HEIGHT - PLOT_BOTTOMBUFFER - 4, PLOT_TOPBUFFER);
    printLabel(_canvas, 0, y, v);
    uint16_t line_y = map(t, 0, ticks-1, ARCADA_TFT_HEIGHT - PLOT_BOTTOMBUFFER, PLOT_TOPBUFFER);
    _canvas->drawLine(PLOT_LEFTBUFFER, line_y, ARCADA_TFT_WIDTH, line_y, TICKLINE_COLOR);
  }
}

void printLabel(GFXcanvas16 *_canvas, uint16_t x, uint16_t y, float val) {
  char label[20];
  if (abs(val) < 1) {
    snprintf(label, 19, "%0.2f", val);
  } else if (abs(val) < 10) {
    snprintf(label, 19, "%0.1f", val);
  } else {
    snprintf(label, 19, "%d", (int)val);
  }
  
  _canvas->setCursor(PLOT_LEFTBUFFER-strlen(label)*6-5, y);
  _canvas->print(label);
}





/**
 * @brief      Printf function uses vsnprintf and output using Arduino Serial
 *
 * @param[in]  format     Variable argument list
 */
void ei_printf(const char *format, ...) {
    static char print_buf[1024] = { 0 };

    va_list args;
    va_start(args, format);
    int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
    va_end(args);

    if (r > 0) {
        Serial.write(print_buf);
    }
}


void TIMER_CALLBACK() {

  int32_t sample = 0;

    if (inference.buf_ready == 0) {
              sample = analogRead(USE_EXTERNAL_MIC);
              sample -= 2047; // 12 bit audio unsigned  0-4095 to signed -2048-~2047
                #if defined(AUDIO_OUT)
                  analogWrite(AUDIO_OUT, (sample+2048)); 
                #endif
              //Serial.println(sample);
            inference.buffer[inference.buf_count++] = (int16_t) sample;

            if(inference.buf_count >= inference.n_samples) {
                inference.buf_count = 0;
                inference.buf_ready = 1;
            }
        
    }
}





/**
 * @brief      Init inferencing struct and setup/start PDM
 *
 * @param[in]  n_samples  The n samples
 *
 * @return     { description_of_the_return_value }
 */
static bool microphone_inference_start(uint32_t n_samples)
{
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));

    if(inference.buffer == NULL) {
        return false;
    }

    inference.buf_count  = 0;
    inference.n_samples  = n_samples;
    inference.buf_ready  = 0;

    // configure the data receive callback
    //PDM.onReceive(&pdm_data_ready_inference_callback);



    return true;
}

/**
 * @brief      Wait on new data
 *
 * @return     True when finished
 */
static bool microphone_inference_record(void)
{
    inference.buf_ready = 0;
    inference.buf_count = 0;

    while(inference.buf_ready == 0) {
        delay(10);
    }

    return true;
}

/**
 * Get raw audio signal data
 */
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr)
{
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);

    return 0;
}

/**
 * @brief      Stop PDM and release buffers
 */
static void microphone_inference_end(void)
{
    free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif
