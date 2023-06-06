# Table of Contents
1. [Journey & Motivation](#journey-&-motivation)
2. [Installation](#Installation)
3. [Documentation](#Documentation)
4. [Contribution](#Contribution)
5. [Setup](#setup)


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
I was fully automate the whole game in 2-3 weeks. I learnt new things about apps and how to automate them. And expecially how to do object detection in through image processing.

From game perspective. I started to auotmate the single level repetititve tasks. Then I realized I can automate some other task which needed manual inputs. So automated how to go to next level. Then I also automated some elements wich gives extra boost.

There were 3 levels of automation in the game:

1. Targetting elements and upgrading the stuff.
2. Automatically move in the UI by sliding events and find the targetted elements if not present in current screen for some time.
3. Moving to next stage and fetching the boosting elements. 

## Installation


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