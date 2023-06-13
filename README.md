# Table of Contents
1. [Journey & Motivation](#journey--motivation)
2. [Installation](#Installation)
3. [Tested System Configuration](#tested-system-configuration)
4. [Documentation](#Documentation)
5. [Contribution](#Contribution)
6. [Setup](#setup)


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


### Project setup

1. First clone the project.
2. Then create pytyhon virtual environement.
3. Then install the required packages through requirements.txt
4. Then run emeulator in android studios. With game running.
5. Now run adb_autoplay.py to run the game.



pip install python-dotenv

The code provided is a script for automating gameplay actions in a game using Python. Specifically, the game appears to be a food-related game, as inferred from the function names and comments. The game might involve upgrading food items, opening chests, checking for in-game ads, and other similar tasks. The script automates these tasks using a mix of screenshot analysis, template matching, and interacting with the game's interface programmatically.

Here is a summary of what the classes and functions in the script do:

Timer: This is a context manager class for timing the execution of blocks of code. It is used throughout the script to measure the time taken to complete various tasks.

AutoEatventure: This is the main class that automates the gameplay. Here are the key methods:

click, click_and_hold, input_text, swipe: These methods perform simple actions in the game interface.

get_better_food_button, get_ad_cross_button, redeem_investor: These methods find specific game elements on the screen and interact with them.

run_full_boost_ads, run_ad: These methods are used to deal with ads in the game.

open_chests, check_to_go_next_level, upgrade_food_items, open_boxes, do_upgrades: These methods handle various aspects of the gameplay, like opening chests, upgrading items, moving to the next level, etc.

login_with_cloud, start_game_for_first_time, init_game, start_playing_game: These methods handle the game's start-up process and the main gameplay loop.

The script finishes with some driver code that creates an instance of the AutoEatventure class and starts the game.

Overall, this script appears to automate gameplay for testing or grinding purposes, which might be useful in a game that requires repetitive actions or long periods of playtime. However, keep in mind that the use of such scripts could potentially violate the terms of service of the game. It's always recommended to check the guidelines of the game and respect the developer's rules and policies.