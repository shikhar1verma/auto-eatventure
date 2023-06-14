[![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) 
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://www.linux.org/) 
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/) 
[![Unity](https://img.shields.io/badge/Unity-100000?style=for-the-badge&logo=unity&logoColor=white)](https://unity.com/) 
<a href="https://opencv.org/"><img src="https://www.vectorlogo.zone/logos/opencv/opencv-ar21.png"  width="8%"></a>

# Table of Contents
1. [Journey & Motivation](#journey--motivation)
3. [Tested System Configuration](#tested-system-configuration)
2. [Installation](#Installation)
6. [Setup](#setup)
4. [Documentation](#Documentation)
5. [Contribution](#Contribution)


## Journey & Motivation

### Motivation
I love incremental games. Not the idle ones. Where almost everything is repetitive after few hours. Where people relegiously put thoughts and efforts. Where after few steps anything can happen. When you reach a stage where there can be multiple paths but the ending will be the same. The small things revealing itself, when you think everything is so repetitive. Like Antimatter Dimensions. Its not the UI/Graphics but the efforts and logic behind the game to make it amusing.

### Journey
So while playing some random game I found through ads this game named Eatventure. This is a slow and very repetitive game. But the upgrades and the chest openings. The updation of character is just amazing. How you boost the gameplay through your character.
The only downside is its very slow and too repetitive. With version 1.7, now its become even slower. Especially to reach the endgame. Though I loved how UI and graphics were made. Minimilistic yet amusing. But like any other guy who played it for like 3 days straight, I realised, I am wasting alot of time. But its fun to play the game. And I want to open the differnt possiblities but fast. I don't wan't to get the moded game just to check out how things go. So as a developer I decided to automate the repetitive tasks.

I never did android app automation. But I did web automation previously to extract technology articles data for an ML project. I was able to extract 5.5 million technology news articles from open news websites. Which are popular and regular source of technology news.

I started exploring how the app automation is done. To my suprise Appium is widely used by people to do automation testing and python can be used to do it. I did all the setup and able to start the app through android emulator in android studios and Appium inspector and client. But it was not a native app of android, it was unity game running in android app. So the major problem was I cannot target the elements of UI code which we generally do in websites or android apps. In android unity app games we have an element which is empty and actual UI code is rendered in unity engine. Whose code cannot be seen as its in machine byte code.

Before I was dropping the idea to automating the repetitive stuff of game. I did another roung of researching. Then I found a solution for targeting the elements in unity games which is altunity drivers using appium. But downside was we need actual source code of unity game to do a element level targetting of UI element.

The last and only way I found by which one can do the automation is through image processing. And I have done some work with openCV for text detection in image pdfs. So I searched and researched. Also did alot of stackoverflow and chatGPT. Then through python adbutils library and ADB of android, I was able to tap general events a person can do in an app through python. The only downside is that it can be slow as we have to take a screenshot then save it on disk then do image process find the elment position and then tap or click the element accordingly. Or may be enter the text. We can automate anything like we do in general native android apps in unity app games. But this targetting of element will not be 100% sure everytime.

Here by targetting an element through image processing, I meant is, we need to do object or element detection in our opened screen. How we do this is, we already have a target element's template ie sub image. This template is the exact resource who we need to target. So what openCv does is, it tries to match the current state ie screenshot with template of targetted image. So it may match 80-100% if template is an exact copy till pixel. So our small template image resource is matched with full screenshot image. And this very cumbersome process. Because many time if you didn't process the images the exact template may not match element in your screenshot.

### Achieved
I was able to fully automate the whole game in 2-3 weeks. I learnt new things about apps and how to automate them. And especially how to do object detection through image processing.

From game perspective. I started to auotmate the single level repetititve task. Then I realized I can automate some other task which needed manual inputs. So automated how to go to next level. Then I also automated some elements wich gives extra boost.

There were 3 levels of automation in the game:

1. Targetting elements and upgrading the stuff.
2. Automatically move in the UI by sliding events and find the targetted elements if not present in current screen for some time.
3. Moving to next stage and fetching the boosting elements. 

## Tested System Configuration

The script was developed and tested on below system configuration:

1. OS: Ubuntu
    ```
    Distributor ID:	Ubuntu
    Description:	Ubuntu 20.04.3 LTS
    Release:	20.04
    Codename:	focal
    ```
2. Programming language: Python
    ```
    Python 3.7.6
    ```
3. Mobile OS used: Android
    ```
    Pixel 6 Pro API 33 tiramisu
    Android 13.0 Google APIs | x86_64
    ```
4. Mobile emulator used: Android studios in built emulator is used
    ```
    # Android studios
    Android Studio Flamingo | 2022.2.1 Patch 1
    Build #AI-222.4459.24.2221.9971841, built on April 19, 2023
    Runtime version: 17.0.6+0-17.0.6b802.4-9586694 amd64
    VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.

    # Emulator 
    Android Debug Bridge version 1.0.41
    Version 34.0.1-9680074
    ```
5. Bridge to connect programming language and mobile emulator: Android Debug Bridge (abbreviated as ADB)
    ```
    Android Debug Bridge version 1.0.41
    Version 34.0.1-9680074
    ```
6. Game version used: Eatventure_1.6.0


## Installation

This installation will be done on ubuntu. But I'll try to tell for windows also. 

Though if you are ios/apple user then you have to find the similar things in apple. We are not running the game in ios mobile. For that feel free to contribute. I don't have apple related products so I can't write the code in it.

We need 3 things to run this automation script:

1. Python (tested on Python 3.7.6)
2. Android studios (latest as of 2023-06-10)
    
    a. To be precise the exact android studios on ubuntu will be. 
    ```
    Android Studio Flamingo | 2022.2.1 Patch 1
    Build #AI-222.4459.24.2221.9971841, built on April 19, 2023
    Runtime version: 17.0.6+0-17.0.6b802.4-9586694 amd64
    VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
    ``` 
    b. And the emulator is 
    ```
    Pixel 6 Pro API 33 tiramisu
    Android 13.0 Google APIs | x86_64
    ```
3. ADB system library. This is to connect python script with android studios emulator.
    ```
    Android Debug Bridge version 1.0.41
    Version 34.0.1-9680074
    ```

### Python Installation

**For Ubuntu**: https://beebom.com/how-install-python-ubuntu-linux/

**For Windows**: https://www.digitalocean.com/community/tutorials/install-python-windows-10

### Android Studios Installation

Just keep in mind while installing android studios that it needs java. So that also be installed. Below links provide that installation also.

**For Ubuntu**: https://linuxhint.com/install-android-studio-ubuntu22-04/

**For Windows**: https://www.makeuseof.com/windows-android-studio-setup/

Once you installed android studios you need to create emulator and understand how to run it. The emulator and the android version we are using is as below:
```
Pixel 6 Pro API 33 tiramisu
Android 13.0 Google APIs | x86_64
```

The tutorial link to create emulator and run accordingly https://youtu.be/GhuiNcOEv1A?t=91

### ADB 

**For Ubuntu**: You can follow the below url or can run the below command: 

Tutorial: https://www.xda-developers.com/install-adb-windows-macos-linux/

Command: `sudo apt-get install android-sdk-platform-tools`

**For Windows**: https://www.xda-developers.com/install-adb-windows-macos-linux/


## Setup

1. First clone the project.
    ```
    git clone https://github.com/shikhar1verma/auto-eatventure.git
    ```
2. Then create python virtual environement.
    
    a. First go to the folder where you want your virtual python environment. Like some folder named "python-environments".
    
    b. Then create the environment.
    
    c. Then activate that environment
    
    ```
    # step a
    cd ~/python-environments/

    # step b (here python environment name is eatventures-env)
    python -m venv eatventures-env

    # step c 
    source ~/python-environments/eatventures-env/bin/activate

    # if want to come out from this python enviroment you can run
    # below command. Right now we don't have to use this command
    deactivate
    ```
3. Then install the required packages through requirements.txt
    ```
    # in the project folder run below command to install all python
    # libraries in you python virtual environment
    pip install -r requirements.txt
    ```
4. Then run emeulator in android studios. With game running.
    
    a. Once your nexus emulator is up and running. We need to install the game version 1.6.
    
    b. Here is the link of apk file download this apk file or any other apk of this game from any website you wish. I installed from apkpure. It was the first link on google search.
    https://apkpure.com/eatventure/com.hwqgrhhjfd.idlefastfood/download/10600-APK-933aa331d5e24bf37bfd9dc4b7b974be

    c. The downloaded apk file must be present in Downloads folder. Drag and drop that folder in emulator it will install the game.

    d. Once game is installed then run the game. Login with your account accordingly. If you don't have account you can register to save your progress so that you can play the game in your mobile later.

    e. Once playable screen is opened now we will be run our python script which will do the magic.

5. To autoplay the game just run below command.
    ```
    python adb_autoplay.py
    ```
    It will run the python script and will interact with the emulator automatically.

    There is one more script autoplay.py that is a failed attempt as I was trying to directly run the game through UI elements.


## Documentation

Here is a summary of what the classes and functions in the script do:

**Timer**: This is a context manager class for timing the execution of blocks of code. It is used throughout the script to measure the time taken to complete various tasks.

**AutoEatventure**: This is the main class that automates the gameplay. 

Here are the key methods:

These methods perform simple actions in the game interface.
 1. click
 2. click_and_hold
 3. input_text
 4. swipe: 
 
These methods find specific game elements on the screen and interact with them.

1. get_better_food_button 
2. get_ad_cross_button
3. redeem_investor 

These methods are used to deal with ads in the game.

1. run_full_boost_ads
2. run_ad 

These methods handle various aspects of the gameplay, like opening chests, upgrading items, moving to the next level, etc.

1. open_chests
2. check_to_go_next_level
3. upgrade_food_items
4. open_boxes
5. do_upgrades 

These methods handle the game's start-up process and the main gameplay loop.

1. login_with_cloud
2. start_game_for_first_time
3. init_game
4. start_playing_game 

The script finishes with some driver code that creates an instance of the AutoEatventure class and starts the game.

## Contribution

Any kind of contribution is welcomed. I will be happy if some new person who just started to code tries to contribute.

Though any level of expertise is welcomed.

Steps to contribute:

1. Open an issue: Discuss about the changes or the improvements you want to do.

2. Approval: If the issue you opened will help project in any way then your issue will be approved for create a PR(pull request) otherwise further discussion will take place.

3. Pull request: All the PR will be accepted if its related to an issue. If PR is raised without an issue then PR will be rejected.

4. PR merge: After reviewing the code the PR will be merged else comments will be giving the code to improve the code.

I copied below guidlines from github:
```
GitHub:
“We want people to work better together. Although we maintain the site, this is a community we build together, and we need your help to make it the best it can be… Respect each other…remember to criticize ideas, not people.

Avoid name-calling, ad hominem attacks, responding to a post’s tone instead of its actual content, and knee-jerk contradiction. Instead, provide reasoned counter-arguments that improve the conversation. If you disagree with someone, try to understand and share their feelings before you address them. This will promote a respectful and friendly atmosphere where people feel comfortable asking questions, participating in discussions, and making contributions. Additionally, communicating with strangers on the Internet can be awkward. Try to use clear language, and think about how it will be received by the other person.”
```

Hope you follow it and help each other in growing.