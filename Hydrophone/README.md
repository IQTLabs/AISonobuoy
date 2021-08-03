# TinyML & Hydrophones

## What are these things?

This is a small effort to look at running ML models against Hydrophone data on an Arduino or similar microcontroller. TinyML focuses on getting machine learning working on these lower power devices. New tools, like [Edge Impulse](https://www.edgeimpulse.com), have made it easy to start building your own ML models. 

Hydrophones are microphones that can capture underwater sounds. You will often see them in movies where they are hunting submarines. There are lots of interesting things you can hear underwater, like fish, volcanos and boats. 

Being able to push audio from a hydrophone through a TinyML model would make it possible to build a self-contained sensor that could detect underwater events.

## What is this?

This work was put together to see if it is possible to detect underwater events on an Arduino. It includes a board for connecting a hydrophone to a microntroller and a small Arduino program that runs an ML model and displays whether a boat was detected.

### Hydrophone Interface Board

This is a Featherwing form factor board that has a 3.5mm jack, a MAX4466 chip and adjustable gain. It outputs the amplified audio out on one of the Feather analog pinouts. Here is a short journey on how the board came to be:

I selected the Aquarian hydrophone to work with. The [H2A model](https://www.aquarianaudio.com/h2a-hydrophone.html) seemed to be rugged and reasonably priced, for a hydrophone. It uses a standard 3.5mm jack, making it easy to connect to a lot of different recorders. 

I haven't worked much with microphones before, so I learned a number of things. First, microphones need a bit of power to work, so they will not work on a "line-in" input. For interfacing with an Arduino, this means that you can not simply hook it up to a GPIO pin and read the signal. You need to put some power through the microphone. Secondly, the actual signal from a microphone is quite faints and needs to be amplified before you can start to work with. 

The good news is that there are lots of existing chips for working with microphones that handle both the power and the gain. The surprising thing though, was that I couldn't find an existing board that had a 3.5mm jack and was designed to be connected to an Arduino. In fact, there wasn't really that much information about recording analog audio, directly from a microphone using Arduino. Most of the microphone breakout boards I found were for MEMS style microphones and most of them put out a digital signal. 

Adafruit does have a nice [breakout board](https://www.adafruit.com/product/1063) that uses a MAX4466 chip to power and amplify a Electret  Microphone. This is a similar type of microphone as the one inside the hydrophone. Adafruit also published a nice [guide](https://learn.adafruit.com/tensorflow-lite-for-edgebadge-kit-quickstart/assembly) on how to connect this microphone to one of their [dev boards](https://www.adafruit.com/product/4200) and how to run a TinyML model against that audio. Sampling the audio is a bit of a brute force approach - you simply set an interrupt and sample the pin at a set interval. As a quick experiment, I removed the microphone from the breakout board, added a 3.5mm jack and was able to record audio from the hydrophone.

One of the great things about Adafruit is that they open source all of their hardware designs. I started with the design files for the Electret Mic Breakout Board, moved them around to fit inside the feather form factor and added a 3.5mm jack.

The resulting board fits nicely on the back of the PyBadge and will work with the large range of dev boards that are in the Feather form factor.

Unfortunately, the audio from the interface board is not as high quality as audio recorded from a digital recorder (Zoom H1n). In order to evaluate performance I used an underwater speaker to playback an audio clip. I placed both the microphone and hydrophone in bucket, to try and make it a little more realistic. 

[Interface Board](media/FeatherWing-Audio-Test.wav)
[Digital Recorder](media/Digital-Recorder.wav)
As you can hear, the audio recorded by the interface board is a little more muffled and has more noise than the audio recorded by the digital recorder. (It is a little jumpy because it is recorded in 1 second segments.)

The difference maybe from the sampling technique used to capture the audio, it is only 12-bits. It is more likely from the design of the interface board. Cleaning amplifying audio is an art... and I am not an artist. Any improvements to the design of the interface board would be greatly appreciated.

### Arduino Program

The Arduino program builds off of the example Arduino program from Edge Impulse for inferencing. It is designed to run on the Adafruit [Pybadge](https://www.adafruit.com/product/4200) or Edge Badge. These are a series of development boards with a SAMD51 Cortex M4F processor and a small TFT LCD screen. 

The example program is written to pull audio from a PDM microphone. I updated it to instead sample from an analog pin. The results of running the model on the audio are displayed on the screen, along with the waveform of the audio. It makes for a compact kit for debugging and evaluating model performance in the field.

## Building an ML Based Boat Detector

Generally, the first step in building an ML model is to collect data and label it. For boat detection, I wanted recordings where there was a boat going by in the water and also recordings where there are no boats present. I captured the recordings using a [Zoom H1n recorder](https://zoomcorp.com/en/us/handheld-recorders/handheld-recorders/h1n-handy-recorder/) and the Acquarian hydrophone. In addition to not being an audio expert, I am also not a boating expert. I learned a couple lessons about boats by trying to make these recordings:

1. Just because a boat is docked and not moving, doesn't mean that it is making boat sounds. It turns out that a pump and maybe a motor will be running even if the boat is docked. This means that it is a bad idea to try and record near a marina, because there will be a lot of background boat sounds, even if nothing is moving nearby.
1. Boats can sound very different. The diesel engine on the water taxi sounds a lot different that the outboard engine on a power boat.

I uploaded the different recordings to Edge Impulse and trained a model. They have recently added an AutoML feature to the platform and using that I was able to train a model that almost perfectly classified each type of audio. This is encouraging, but also suggests that I may need more audio and more variety.

## Results 
I did some field evaluation and the system is able to detect nearby boats. More testing is need to see how it would perform in different bodies of water besides a river. Additional training data should help improve performance and allow the model to generalize to a broader range of boats and conditions. Improvements to the interface board should also improve performance.

An Arduino library that includes this model is included. I will look to added the recorded audio to the repo in the future.

## Contact

If you have questions or advice, please reach out to me (Luke Berndt) -> lberndt@iqt.org