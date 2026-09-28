# DivyaChakshu
### AI-Powered Visual Assistance for the Visually Impaired

**DivyaChakshu** is an assistive technology project designed to help visually impaired users understand their surroundings through AI-powered visual interpretation and audio feedback.

The project explores how a camera and artificial intelligence can work together to describe nearby objects, scenes, and useful environmental information in a simple, accessible way.


## Project Overview

People with visual impairments may face difficulties identifying objects, understanding unfamiliar surroundings, and accessing visual information independently.

DivyaChakshu aims to address this challenge by converting visual input into spoken descriptions. The system captures an image of the user's surroundings, processes it using an AI vision model, and provides the resulting information through audio feedback.

The long-term goal is to develop a practical, portable, and user-friendly assistive device.

## Key Objectives

- Provide spoken descriptions of the user's surroundings.
- Help users identify objects and understand scenes.
- Explore AI-based visual assistance using accessible hardware.
- Develop a system that can eventually be adapted into a portable device.
- Keep the user experience simple and accessible.

## System Architecture

The proposed workflow is:

1. **Visual Input** – A camera captures the surrounding environment.
2. **AI Processing** – The captured image is processed by a vision-language model.
3. **Scene Interpretation** – The model generates a description of the visual scene.
4. **Audio Feedback** – The description is converted into spoken output for the user.


Camera
  ↓
Image Capture
  ↓
AI Vision Model
  ↓
Scene Description
  ↓
Audio Feedback
  ↓
User
Project Status

#######DivyaChakshu is being developed as a proof of concept (POC).########

The current work focuses on exploring and testing the software pipeline for image input, AI-based scene understanding, and audio feedback. Further development is required to improve reliability, usability, response time, and portability.

Technologies

The project explores the use of:

Python

Computer vision

Vision-language models (VLMs)

Image capture and processing

Text-to-speech / audio feedback

Local and cloud-based AI inference

Specific models, libraries, and hardware may change as development continues.

Repository Contents

This repository contains selected project source files and documentation.

Some development resources, datasets, model files, local environments, and private configuration files are intentionally excluded from the repository. They may be required separately to reproduce or run particular experiments.

#Future Scope

Possible future improvements include:

1- A compact, wearable or attachable device.

2- Improved scene descriptions and object recognition.

3- Faster and more reliable AI processing.

4- Offline or edge-based inference where feasible.

5- Improved audio interaction and user controls.

6- Additional accessibility-focused features.

7- User testing and evaluation in real-world environments.

#Limitations and Safety

DivyaChakshu is an experimental assistive technology project and is not a certified mobility or safety device.

AI-generated descriptions may be inaccurate, incomplete, or delayed. Users should not rely on the system as a replacement for a cane, guide dog, mobility training, or other established safety practices.

The project will be thoroughly tested carefully before any real-world use.

#Privacy

Images captured by a camera may contain sensitive personal or environmental information.

Users should understand where images are processed and whether they are transmitted to an external service. Private keys, API credentials, certificates, and other sensitive configuration files will not be committed to this repository.

#Developer & Credits

Developed by: Naitik Srivastava
B.Tech – Electronics and Communication Engineering
Babasaheb Bhimrao Ambedkar University, Lucknow


#Disclaimer

DivyaChakshu is an academic and experimental project developed for learning and prototyping. It is not intended to replace professional assistive devices or guarantee user safety.
