import api
from utils import get_new_uid


class InlineObject(object):
    def __init__(self, dict):
        self.__dict__ = dict


def create_img_obj(filename):
    return InlineObject({'filename': filename, 'uid': filename.split('.')[0]})


def init_db_data():
    name = 'name'
    desc = 'desc'

    board_id = 'board_id'
    post_id = ('post_id',)
    reply_id = 'reply_id'
    parent_reply_id = 'parent_reply_id'
    text = 'text'
    img = 'img'
    user = 'user'
    ip = 'ip'

    filename = 'filename'
    uid = 'uid'

    home = '127.0.0.1'

    boards = [
        {
            name: 'Music',
            desc: 'Discuss sound, lyricism, artists, venues, etc. here. Any aesthetic or post related images welcome.',
        },
        {
            name: 'Technology',
            desc: 'For anything and everything relating to technology. Images should relate to your post.',
        },
        {
            name: 'Art',
            desc: 'Sharing and discussion of visual artwork, photography included.',
        },
        {
            name: 'Film',
            desc: 'Discussion of movies and t.v. shows. Images should relate to your post.',
        },
        {name: 'Random', desc: 'Anything goes. Site rules are still enforced.'},
    ]
    for b in boards:
        api.create_board(b[name], b[desc], None)

    posts = [
        {
            board_id: 1,
            text: """Autumnal days feel exceptionally short in Abbotsford, BC, Canada. The sun rises but hardly invites. The inevitability of night is impending.

As 2012 came to a close, Teen Daze entered a state of repose. He chose the company of insular, droning ambient music. He wrote new material, and for the first time he found the process not to be a means of escape or refuge. Rather than imagining an outward utopia, or seeking an inward sanctuary, he simply engaged his work with his reality, his physical world.

Like its namesake, Glacier is more than solidified water adrift in a sea of home-produced electronic music. It is a collection of moments, historical particles and physical experiences, gathered into a whole. A testament to self-editing and sequencing, the 40-minute album merges hours of abstract instrumental work with more structured compositions. Varied yet cohesive, Glacier finds Jamison confident both as a drifter and a romantic. Lyrics are used personally and sparingly, often drifting in and out on a single phrase. "No one sees you, the way I see you", he repeats through opener "Alaska". Album centerpiece "Ice On The Windowsill" celebrates the notion of remaining indoors with the one you love as the world frosts over. Connecting each epiphany are wordless ruminations—like the twisted pitch of "Tundra", the cool warmth of "Forest At Dawn"—some of the most evocative sound design in Teen Daze's career to date. "Walk" is the rightful closer, an affectingly repetitious four chord salute to a fallen day.

The album's fixation on manifesting physicality translates to being a highly performative production. The role of live instruments, field recordings, and general human presence is evident in these songs, just as millennia-old organisms lay suspended in a frozen core. This was a deliberate choice; Teen Daze plans to tour in support of the release for the first time as a full band—essentially to actualize Glacier in the physical world.

https://teendaze.bandcamp.com/album/glacier""",
            img: create_img_obj('glacier.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 1,
            text: """All Of Us, Together is the first proper full-length from Vancouver's Teen Daze. Arriving after a prolific stretch of EPs, singles, and remixes since 2010, and recorded in the hopeful turn from spring to summer 2011, it's something of a culmination. "I'm very proud of this as my first real LP, and the statement it makes. It fully represents where I've come to as an electronic artist."

Teen Daze's music has always suggested an auditory utopia; this album now propels those aesthetic notions forward in the timeline, resulting in a present moment awareness, rather than trademark nostalgia. "I came upon an old book at a thrift store called Utopian Visions, an encyclopaedic volume of different views on what utopia might look like, which became a huge inspiration. Especially when considering the future of our world as it actually unfolds. We're becoming more and more self-reliant, more and more separated from our communities. I wanted to make a record that sounded more synthetic but also inviting-this is futuristic music with a heart."

It won't take long to hear it as his purest form electronic work to date. Spacious opener "Treten" introduces a pulse that runs throughout Together, sometimes resting in warmth ("Hold", "For Body and Kenzie"), other times reaching for the smoke-filled ceiling of a club ("Erbstück", "Brooklyn Sunburn"). Perhaps these tracks feel so alive and communal because they were arrived at through performance. "I played a lot of this material on tour last year, and there's a connection to that element, it's all become very dear to me."

"Together" is the key word here. This is a record meant for interaction, be it on the dancefloor or on a drive under the night sky with friends. "There are countless reasons on why a person would create something; my reason is bring people together, to let them know that they're not alone."

https://teendaze.bandcamp.com/album/all-of-us-together""",
            img: create_img_obj('all_of_us,_together.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 2,
            text: """You mean you haven't looked at the 2020 development survery before investing in that???
        
        https://insights.stackoverflow.com/survey/2020""",
            img: create_img_obj('stacko.png'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 3,
            text: """A visceral shot atop the Three Gorges Dam.""",
            img: create_img_obj('three_gorges.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 3,
            text: """Ahhhhm

8/29/91

10:55 PM

This is part of a journal entry.

Slow at the track today, my damned life dangling on the hook.
I am there every day. I don't see anybody else out there every
day except the employees. I probably have some malady. Saroyan
lost his ass at the track, Fante at poker, Dostoevsky at the
wheel. And it's really not a matter of the money unless you run
out of it. I had a gambler friend once who said, "I don't care
if I win or lose, I just want to gamble." I have more respect
for the money. I've had very little of it most of my life. There are
only two things wrong with money: too much or too little.

Well, I suppose there's something out there we want to
joggle ourselves with. At the track you get the feel of
the other people, the desperate darkness, and how easy they
toss it in and quit. The racetrack crowd is the world brought
down to size, life grinding against death and losing. Nobody
wins finally, we are just seeking a reprieve, a moment out of
the glare. (shit, I just burnt the end of my finger with a
cigarette. I was musing on purposelessness. That
woke me up, brought me out of this Sartre state!) Hell, we
need humor, we need to laugh. I used to laugh more. I used to
do everything more. Now, I am writing and
writing and writing. The older I get the more I write, dancing
with death. Good show. And I think the stuff is all right. One
day they'll say, ... dead, and then I will be truly
discovered and hung from stinking bright lampposts. So what?
Immortality is the stupid invention of the living. You see
what the racetracks does? It makes the lines roll. Wax, lightning
and luck. The last bluebird singing. Anything I say sounds
fine because I gamble when I write. Too many are too careful.
They study, they teach and they fail. Convention strips them
of their fire.

I feel better now, up here on this second floor with the Macintosh. My pal.
And Mahler is on the radio, he glides with such ease, taking big chances,
one needs that sometimes. Then he sends in the long power rises.
Thank you, Mahler, I borrow from you and can never pay you back.

I smoke too much, I drink too much but I can't write too
much, it just keeps coming and I call for more and it arrives
and mixes with Mahler. Sometimes I deliberately stop myself. I
say, wait a moment, go to sleep, or look at your 8 cats, or sit
with your wife on the couch. You're either at the track or
with the Macintosh. And then I stop, put on the brakes, park
the damned thing. Some people have written that my writing has
helped them go on. It has helped me too. The writing, the
roses, the 8 cats, my wife.

There's a small balcony here, the door is open and I can
see the lights of the cars on the Harbor Freeway south, they
never stop, that roll of lights, on and on. All those people.
What are they doing? What are they thinking? We're all set
to die, all of us, what a circus! That alone should make us
love each other but it doesn't. We are terrorized and
flattened by trivialities, we are eaten up by nothing.

Keep it going, Mahler!
You've made this a wonderous night.
Don't stop, you son-of-a-bitch! Don't stop.

https://www.youtube.com/watch?v=FXii0aY0-zI""",
            img: create_img_obj('buk.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 4,
            text: """It's not hippie witch, it's Twin Peaks, and it's very in.""",
            img: create_img_obj('90210.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 4,
            text: """.""",
            img: create_img_obj('brandon.png'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 4,
            text: """I was very talkative when I was small. But at age five, I ate a can of pineapple that had expired, and I stopped talking. For that reason, I have very few friends.
            >end of story two""",
            img: create_img_obj('fallen_angles_1995.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 5,
            text: """The curry looks great, let's dig in!""",
            img: create_img_obj('dine_time.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            board_id: 5,
            text: """Because of its great distance from the Sun, Neptune's outer atmosphere is one of the coldest places in the Solar System, with temperatures at its cloud tops approaching 55 K (−218 °C; −361 °F).""",
            img: create_img_obj('neptune.jpg'),
            user: get_new_uid(),
            ip: home,
        },
    ]

    for p in posts:
        api.create_post(p[board_id], p[text], p[img], p[user], p[ip])

    replies = [
        {
            post_id: 1,
            text: """I have come to to wound the autumnal city. (Dhalgren 1975)""",
            img: None,
            user: get_new_uid(),
            ip: home,
        },
        {
            post_id: 9,
            text: """.""",
            img: create_img_obj('oo.gif'),
            user: get_new_uid(),
            ip: home,
        },
    ]

    for r in replies:
        api.create_reply(r[post_id], r[text], r[img], r[user], r[ip])

    reply_to_reply = [
        {
            post_id: 1,
            parent_reply_id: 1,
            text: """The main character of that book, like the author, is possibly intermittently schizophrenic. The novel's narrative is intermittently incoherent (particularly at its end), the protagonist has memories of a stay in a mental hospital, and his perception of reality and the passages of time sometimes differ from those of other characters. Over the course of the story he also suffers from significant memory loss. In addition, he is dyslexic, confusing left and right and often taking wrong turns at street corners and getting lost in the city. It is therefore unclear to what extent the events in the story are the product of an unreliable narrator.""",
            img: create_img_obj('dhalgren.jpg'),
            user: get_new_uid(),
            ip: home,
        },
        {
            post_id: 1,
            parent_reply_id: 3,
            text: """That explains a lot""",
            img: create_img_obj('oo.gif'),
            user: get_new_uid(),
            ip: home,
        },
    ]

    for rr in reply_to_reply:
        api.create_reply_to_reply(
            rr[post_id], rr[parent_reply_id], rr[text], rr[img], rr[user], rr[ip]
        )
