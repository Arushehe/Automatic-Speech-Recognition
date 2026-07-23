# Research — Track A (ASR)

## 1. ASR Pipeline Overview
Automatic Speech Recognition (ASR) is the process of transcribing spoken language into text. Their are a series of steps followed in ASR structure, each one dealing with its own aspect of the process of speech recognition. Starting with the audio input, the system goes through a gradual extraction of useful information, recognition of speech patterns, language understanding, and ultimately the generation of text.
Here is the whole ASR workflow:
```
Speech
   │
   ▼
Preprocessing
   │
   ▼
Feature Extraction
   │
   ▼
Acoustic Model
   │
   ▼
Language Model
   │
   ▼
Decoder
   │
   ▼
Recognized Text
```
The role of each step is described below:
Step	                       Description
Preprocessing	               Normalizes the audio by transforming it into a standard format 
                             appropriate for the ASR task.
Feature Extraction	         Transforms the audio signal into meaningful speech features which can 
                             be then used by ml algorithms.
Acoustic Model	             Learns the mappings between speech features and speech sounds/tokens/characters.
Language Model	             Does the recognition by choosing the best words sequence using the 
                             language context and understanding the meaning.
Decoder	                     Generates the transcription using the results of the previous steps.


## 2. Feature Extraction
Feature extraction is the procedure of transforming the raw audio into a form that can be understood by an ASR model. Instead of using the raw audio itself, important speech data is extracted, while the rest of the data is filtered out.
The audio is first transformed into a spectrogram, which shows how frequencies vary over time. The Mel Scale is then applied to the spectrogram to create a Mel Spectrogram(which contains a more human like perception). At last, a log transformation is done to create a Log-Mel Spectrogram, which serves as the input for ASR models like Whisper.
The MFCCs features are traditionally used by ASR systems, while deep learning models use the Log-Mel Spectrograms as they contain more speech data.
Raw Audio --> Spectrogram --> Mel Spectrogram --> Log-Mel Spectrogram --> Whisper

## 3. Acoustic Model vs Language Model
The Acoustic Model recognizes speech sounds from the features obtained from the audio. The main goal of the acoustic model is to learn the relationship between speech and linguistic unit (phonemes, characters, or tokens). The main function is to recognize & understand what has been said from the audio signal only.
The Language Model enhances transcription by using grammar and context to find out the most probable word sequence in the sentence. Also, it can distinguish words that may sound the same. For an example, it can differentiate between "I scream" and "ice cream" depending on the context of the sentence.
In classical ASR systems, the Acoustic and Language models are two independent parts of the pipeline. However, in the current end-to-end models such as Whisper, both functions are performed by a transformer-based model.
|Acoustic Model                          |	Language Model                      |
|----------------------------------------|--------------------------------------|                          
|Processes speech/audio features	       |  Processes text and language context |
|Recognizes speech sounds	               |  Improves sentence accuracy          |
|Predicts phonemes, characters, or tokens|  Predicts word sequence              |
|Recognizes "What was spoken?"	         |  Recognizes "What makes sense?"      |

## 4. Decoder
The Decoder is the final component of an Automatic Speech Recognition System which produces the final transcription. The Decoder uses the data from both Acoustic Model and Language Model to create the most likely sequence of words. The decoder produces the output which includes the next predicted text based on the sounds recognized and the language context.
Modern end-to-end ASR models like Whisper have their decoder inside the transformer model and produce the transcription one token at a time till the sentence is completed.
Acoustic model + Language model + Previous context --> Decoder --> Predicts the next token for the sentence

## 5. Whisper (OpenAI)
Whisper is an open-source Automatic Speech Recognition (ASR) model designed by OpenAI. It is a transformer-based encoder-decoder model trained on a massive and diverse multilingual speech dataset. Whisper has the capability of performing speech transcription, speech recognition, and speech translation tasks. Unlike normal ASR models that use Acoustic Models and Language Models separately, Whisper is an end-to-end ASR model that learns speech recognition and language understanding inside one neural network. It uses Log-Mel Spectrogram as its input data, runs it through the transformer encoder and generates transcription through a transformer decoder.
Whisper is popular because it performs well on noisy audio, different accents, and multiple languages without being specially trained for specific tasks. OpenAI offers different sizes of the model (Tiny, Base, Small, Medium, and Large) that allow users to choose either fast processing or high transcription quality based on their application needs.
Key Features :
An open-source ASR model designed by OpenAI.
Performs multilingual speech recognition.
Has the ability to perform speech transcription and translation.
Transformer-based encoder-decoder architecture.
Uses Log-Mel Spectrograms as input data.

## 6. Offline vs Streaming ASR
The automatic speech recognition models can be classified into offline ASR and streaming ASR based on their working mechanisms:
The offline ASR works on the recorded audio by processing the whole audio recording. The high transcription accuracy is achieved in this type due to the availability of the whole speech and hence it is useful in scenarios like meeting transcriptions, podcasts, recorded interviews etc.
The streaming ASR works on the ongoing audio where transcription is done in real-time with very low latency. The use of the streaming ASR is found in voice assistants, live captions, customer services and other voice control apps. Even though the response from the streaming ASR is faster, the accuracy may be slightly less as the future speech is not known.
Comparison:
`Offline ASR`			                              `Streaming ASR`
Complete audio processing after recording			On-the-go audio processing
High transcription accuracy			              Low response time (low latency)
Useful in recorded audio			                Useful in live scenarios
Example: Meeting transcription			          Example: Siri, Alexa, Live Captions

## 7. Multilingual ASR Challenges
Automatic speech recognition systems should be able to transcribe speech that is uttered by people who speak various languages with different accents. In this way, speech recognition becomes a more difficult task than when a system deals only with one language.
Some of the issues that may arise during ASR are accent differences, combining different languages in the same phrase(for an example when people speak Hinglish in india), background noise, and insufficient amount of data for low resource languages. The accuracy of transcription can be decreased by these features if the model was not trained on varied speech samples.
Whisper solves many of these issues through its training on large scale multilingual datasets that include speeches of different languages, accents, and recording conditions.
Common Issues:
Differences in accents and pronunciations
Using different languages in a single conversation
Background noise
Low-resource languages with insufficient amount of data
Different speeds of speech

## 8. Comparison of Open-Source ASR Models
There are different ASR models which have different architectures and unique features. The most commonly used ASR models are Whisper, Wav2Vec 2.0 and DeepSpeech. Although all the three ASR models convert speech to text, they differ in their accuracy and other characteristics.
`Feature`	           `Whisper`	              `Wav2Vec 2.0`           `DeepSpeech`
Developer	           OpenAI	                  Meta (Facebook AI)	    Mozilla
Architecture	       Transformer              Transformer-based	      RNN-based
                     Encoder-decoder 
Input	               Log-Mel Spectrogram	    Raw audio	              MFCC features
Multilingual supp.	 Yes	                    Limited	                Limited
Noise handling	     High	                    Moderate	              Moderate
Best use case	       General-purpose          Fine-tuned speech       Lightweight speech 
                     multilingual ASR         recognition             recognition
For this project, Whisper makes the most sense because it handles noise well and doesn't require heavy fine-tuning like Wav2Vec 2.0 does.

## 9. Whisper Model Sizes
OpenAI has provided various models for Whisper based on the difference in their speed and transcription quality. Smaller models run faster and have less computation needs, while the larger models are expected to provide better transcription accuracy.
`Model`	    `Speed`	     `Accuracy`	             `Use of Recommendation`
Tiny	      Very fast	    Basic	                 Real-time use cases and low resource device
Base	      Fast	        Good	                 For general purpose transcription
Small	      Moderate	    Better	               For balance speed and accuracy
Medium	    Slower	      Higher	               Higher accuracy transcription
Large	      Slowest	      Highest	               Highest accuracy transcription
Selection of model is based on the application. Smaller models are selected where inference speed is critical, but larger models are selected where transcription accuracy is the most important factor.

## 10. WER (Word Error Rate)
Word Error Rate (WER) is the most common technique adopted to measure the efficiency of an Automatic Speech Recognition (ASR) system. The word error rate calculates the degree of similarity between the original spoken text and the transcription by quantifying the errors.
There are three kinds of errors:
Substitution (S): The replacement of one word with another.
Deletion (D): Failure to include a word from the original sentence.
Insertion (I): The inclusion of additional words.
Word Error Rate (WER) is calculated like this:
WER = (S + D + I) / N
Where N represents the total number of words in the reference sentence.

---


