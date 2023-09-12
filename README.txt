README

for 

Dead By Zombie

ver 1.1

"Day is for the Living,
Night is for the Dead"
------------------------

This is an open source snapshot of my 100% originally-created but previously close-sourced, commercial Python-based Rogue-like game about a zombie apocalypse, Dead By Zombie. The official public repo is:

    https://github.com/mkramlich/Dead_By_Zombie

I'm not taking code contributions at the moment, so don't bother issuing pull requests. Feel free to email with questions, suggestions or requests.

We also used to officially support Windows but have dropped that platform as not worth the effort. The creator prefers and therefore focuses on the Linux and Mac ecosystems. Trust me: life's better with Mac or Linux.

Feel free to play it. And feel free to make modifications to the code that run only on your own machine. You may not distribute this game, its code or your own modified versions of it to other parties without my explicit prior permission. Feel free to throw compliments/insults at me to my email address). I also love LEGO. And Advanced Squad Leader. I hate mustard. Best compliment is LEGO. Worst insult is mustard. Though technically I can eat mustard, so maybe that's only the 2nd worst insult?

All rights reserved worldwide. (This means you, Kansas. *cough*)


Requirements:

The game comes in versions for different platforms: Mac and Linux. The requirements vary by platform:

    on Mac:
        Mac OS X 10.5 or higher
            or
        Mac OS X 10.4 (or less might work), with Python 2.7 (accessible via "/usr/bin/env python2.7")

    on Linux:
        Linux 2.x (tested on 2.6), with Python 2.7 (accessible via "/usr/bin/env python2.7")

The Mac version gets the most testing since it is the developer's primary workstation. Linux is similar to Mac so will probably work second best.


Mac Instructions:

To play the game:

    * in the Dead_By_Zombie folder, double-click on the file 'play-game.sh' (or run it in Terminal)
    * on the Intro screen you'll see a menu of choices
    * use the up/down arrow keys to move the cursor up/down
    * select the highlighted choice by pressing SPACEBAR


Linux Instructions:

Similar to Mac, but since you're a Linux user you'll likely have the tech skills to figure things out. The play-game.sh script should start the game just like in the Mac version. Python versions higher or lower than 2.7 might work fine, but you'll have to adjust paths/aliases/scripts on your own to make it work in your particular environment.


Platform Common Instructions:


To save the game while playing:

    * hit 'S' (uppercase) then wait. After a second or so it will tell you it has finished the save, and then you can hit any key to resume playing

To load a previous save while playing:

    * hit 'L' (uppercase) then wait. After a second or so it will tell you it has finished the load, then hit any key to begin playing from that point.

To quit the game:

    * hit 'Q' (uppercase) when in the default mode
    * if you wish, close the Terminal window by clicking on the little red circle icon at the top-left corner of the window

To restart the game with a fresh campaign:

    * on the Intro Screen's menu move the cursor to Restart Game
    * press SPACEBAR

To uninstall the game:

    * make a backup copy of your saved game files (OPTIONAL)
    * delete the DeadByZombie folder

Just so you know, saved games are stored in files in the DeadByZombie/saves folder. Feel free to make a backup copy of them somewhere if you wish to de-install the game, but possibly re-install it later and still be able to continue playing from where you left off.

HOW TO PLAY

Your goal is survive and not become a zombie!
Also it would be nice if the rest of humanity survives as well.
A bonus goal would be to see that the zombie menace ends.

The two main ways of dying are by starvation, or being attacked and killed by a zombie -- which then turns you into a zombie!

The best way to ward off starvation is to find and eat plenty of food, whenever needed. Eating adds food to your stomach. Your body digests a little stomach contents over time. When your stomach becomes empty, you begin starving. When you starve, you lose a little HP each tock until you die. There are a variety of sources of food including loot (food laying around in buildings or on the ground), grown food (such as from fruit trees), and the remains of dead lifeforms (corpses). Due to the zombie menace you generally want to stay hidden inside buildings behind close doors. However the need to get new food may force you to go on missions outside to replenish your supply.

You heal naturally, a little per tock, if your cur HP is high enough, compared to your max/normal HP. If you are seriously hurt you won't heal naturally, and in that case your only recourse is to use healing items such as first aid kits, bandages and medicine.

Most actions you perform (such as walking) cause time to pass. Not all actions do. You can tell that time has pased if the Tock value (shown on the main screen) increases. Over time, the world goes through a natural cycle of day and night, and since the ambiant light fluctuates due to that, the range at which you can see will change over time as well. Also, zombies are more active and more likely to spawn, at night. Due to that fact, plus the limited range of vision, night is the most dangerous time of day, especially if outside.

Stairs look like < or >. You may take them up/down to wherever they lead. Taking stairs down may lead into a basement or sewer level. Taking stairs up may lead to a higher floor within the same building you're currently in.

To travel to a different region entirely, follow a route. A route looks like /. It may lead to a nearby part of town, a different neighborhood, into the wilderness, or some other strange and mysterious location worth exploring.

On the main game play screen (called Default Mode), at the bottom, it shows Feedback. This is a bunch of information about events that have occured, things seen nearby, sounds heard, actions witnessed, things experienced, things you've done, and so on. If you see "MORE" in the lower-right corner of the screen it means that there is more Feedback lines that can be shown on screen at once. To see all of them, hit 'f' to go to the Feedback screen. On that screen you can move the cursor up/down to scroll through all the messages.

To pass a little time not doing anything:
    SPACEBAR

To make your character walk somewhere, hit any of these keys to move one step in that direction:
      u   i   o
      j       k
      n   m   ,

Also, on any screen where there's a cursor you can move the cursor up/down with the up or down arrow keys.

To go to a screen mode showing all Feedback:
    f
    NOTE:
        On the Feedback screen, you can move the cursor up/down between entries and pages.
        Hit Space or Return to leave this screen.

To re-read the background story, and see the status of goals and plots:
    t

To pickup one item from the ground in your same area:
    p
    You can then move the cursor up/down between entries and pages until it's focused on the item you want to drop. Then SPACEBAR to drop it. Any other key to exit this mode without doing anything. All similar screens work the same way unless said otherwise.

To pickup all items on ground:
    P

To wield item in inventory, 'w', then move cursor to select the item, then SPACEBAR to wield it.

To unwield item in inventory, 'u', then move cursor to select the item, then SPACEBAR to do it.

Barricades are like walls in that they block movement. You can build a barricade with the 'b' key, followed by the direction to build it in. You must be carrying wood to build a barricade and one wood is consumed per barricaded cell you build. Like walls, barricades can be destroyed, though they are weaker than walls. They can be useful in providing shelter and protection from the zombie menace.

Zombies can sneak up on you from almost anywhere. Well, almost anywhere. If you search and study a spot very carefully you can become sure that no zombies can appear there (hiding under a bed, or up through a trapdoor in floor, or from a ceiling vent, etc.). Use the 'Z' command followed by a direction arrow to search & secure a spot in this manner. This 'search & secure' activity is especially useful in combination with barricades you construct, especially if you want to seal off a shelter or add more living space to an existing building. Beware though: nothing is safe forever.

To wear an item, 'z', then select with SPACEBAR.
To unwear an item, 'x', then select with SPACEBAR.

Here's a full list with brief descriptions:

----------------------|---------------------------------------------------------
` - menu              | returns to the Intro Screen's main menu
                      |
S - save              | will immediately begin saving the game to 'quicksave' file; may take a few seconds to do so be patient; once it finishes saving, it will go to a screen telling you so. then hit any key to resume playing; also, if you later Quit the game, then PLAY a new session it will also resume from the state recorded in that 'quicksave' file
                      |
L - load              | loads game from 'quicksave', then resumes play
                      |
Q - quit              | quits app instantly, without saving
                      |
SPACEBAR - wait       | do nothing for a little bit (for 1 tock)
                      |
arrow keys            |
  or                  |
numbers (as keypad)   |
  or                  |
u/i/o/j/k/n/m/ - move | walk one step in that direction
                      |
f - feedback          | see all current feedback, in a scrollable list
                      |
t - story/status      | read background story and the status of goals and plots
M - memories          | recall remembered things
K - skills            | see your skills
l - look              | goes to screen listing all things in your spot
y/I - inventory       | goes to screen listing all carried items, scrollable
e - eat               | then select item and press SPACEBAR to eat it
h - heal              | then select item and press SPACEBAR to use it
R - read              | then select item to read (a book, document, flyer...)
p - pickup            | pickup an item from the ground
P - pickup all        | pickup ALL items from ground
d - drop              | drop an item (also unwields/unwears it if applicable)
z - wear              | wear an item
x - unwear            | unwear an item (take off if worn; but does not drop)
w - wield             | wield an item
u/U - unwield         | unwield an item (does not drop)
a - attack            | then press dir key, and you'll attack in that dir
o/O - open            | then press dir key, and you'll open door in that dir
c - close             | then press dir key, and you'll close door in that dir
b - barricade         | then dir -- builds a barricade there
Z - search & secure   | then dir -- ensures is safe/secure from zombies
r - route             | follow the route in your area, going to a new location
s - stairs            | take the stairs in your area, to some level above/below
A - ask to stay       | then press dir key towards NPC to address
B - ask to not stay   | then press dir key towards NPC to address
F - ask to follow     | then press dir key towards NPC to address
G - ask to not follow | then press dir key towards NPC to address

Map Key

Here's a key to the most common subset of map entities you'll encounter early:
@ you
P person (fellow human, resident of town, or so-called NPC)
Z zombie
d dog
T tree
% food or corpse or organic material
$ money (cash, gold, valuables)
# wall or major obstacle/barricade
+ closed door
O open door (capital O)
0 window (zero)
/ route, path, passage
< stairs leading up
> stairs leading down
. ground or floor
? unseen or unknown area

Other letters represent other things. Typically, more specific types of people, creatures or items.


HOW TO PURCHASE THE GAME

You no longer can. You may see refs to Demo vs Premium/License but we'll be removing that distinction over time.

However, if you would like to throw a tip/donation at me, or otherwise support my development of new Rogue-like game play, check out my new "Slartboz" project. More details on that down below.


thanks,

Mike Kramlich
Dead By Zombie's Chief Mad Scientist

--------------------------------------------------

UPDATE: 2023 September 12

About 15 years after releasing my first commercial Rogue-like game I've returned to the field.

Slartboz is my new Rogue-like game, under active development, and my de facto sequel and successor to Dead By Zombie (DBZ). Please check it out, starting over at:

    https://github.com/mkramlich/slartboz-pub

FAQ

Q1. how is Slartboz (SB) diff from DBZ?
    * SB is written in Golang. DBZ in Python
    * SB has a real-time engine. NOT a turn-based/you-go-they-go like in DBZ
    * richer color palette used (millions of hues/shades, all across the spectrum -- NOT just the 8 or so "Terminal screen colors" used in DBZ)
    * UI uses Unicode/UTF-8 glyphs, in *addition* to ASCII/ANSI
    * has sound & music
    * private code base, closed source
    * however... small pieces of the code WILL be shared as new, standalone, public FOSS repos, and where their functionality is generic enough. NOT the full source to SB, like I ultimately did with DBZ. The first little piece HAS been shared out, already (a 100% FREE Golang lib for latency instrumentation and reporting), over at: https://github.com/mkramlich/latlearn
    * sci-fi, future, post-apoc setting. Normerika in the year 2100 CE. A weird, terrifying but Fun (TM) world replate with Lazers! Mutants! Robots! Mad AI's! Gigantic Cybernetic Battle Tanks! Wacky Rube Goldberg Devices And Ouroboros Contraptions! Orwellian Levels of Creepy, Dystopic Propaganda Cults! Surveillance Capitalism Gone Overboard! Democracy Collapse! Climate Out of Control! Elong Mux Actually On The Planet Mars! A Certain Ex-President/Ex-Con Living The High Un-Life in Secret Traitorous Exile Somewhere in Grussia ("Sad! Everybody is saying so! Big men, they come up to me! Straight out of central casting!" *shamble-shamble-groan-drool*)

Q2. ok... but what is the same?
    * I made it
    * homegrown engine
    * Rogue-like
    * some randomly-generated (at runtime) content AND some procedurally-generated
    * some plots and some sandbox play
    * UI composed mainly of ASCII glyphs, and runs assuming in a Terminal. like a typical curses-based program (like vim and top). like NetHack, and (the original) Dwarf Fortress
    * I could NOT in good faith call it my de facto "sequel" to DBZ without SB having, oh, say, I dunno... absolutely M-M-M-MASSIVE Z-Z-Z-ZOMBIE H-H-H-HERDS!!!
    * and so.. it does! :-P

------------------------------------------------

SLARTBOZ: Fazzmagik Tales in The Sleen Groove
    coming soon to theaters near you (*)

    (*) not legal in all jurisdictions (*glares at the remote Pacific island of Kiwi, always the rebel*)

