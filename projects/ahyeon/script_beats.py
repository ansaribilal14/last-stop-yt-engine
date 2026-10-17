#!/usr/bin/env python3
"""script_beats.py — 'Ahyeon: The 5th Gen It Girl'  (projects/ahyeon)
Target: 30:00 (1800s) · fact-gated to research/FACTS.md (refs per beat)
Beat kinds: clips (montage pool) | card (typography over looping clip)
Every text block = one narration paragraph = one TTS run.
"""
BEATS = []

# ---------------- ACT 0 — COLD OPEN (~95s) ----------------
BEATS += [
dict(id="co1", act=0, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["batterup", "sheesh", "choom"], refs=["F009", "F010", "F001"],
     text="On November 15th, 2023, YG Entertainment posted a notice that stopped a fandom cold. Their most anticipated trainee — the girl fans had already crowned before she ever officially debuted — would not be in the group's first music video. Six members would go on without her. One would stay behind, unnamed, in a building full of mirrors. What happened next is the strangest debut arc in modern K-pop: a group that broke YouTube records without its center, a record label that refused to replace her, and a nineteen-year-old who came back from the edge of erasure to become the defining idol of her generation. This is the story of Jung Ahyeon — and why the industry now calls her the fifth generation's it girl."),
dict(id="co2", act=0, kind="card", card=dict(kind="title",
     lines=["AHYEON", "THE 5TH GEN IT GIRL"]), refs=["F001"],
     text="Ahyeon. The fifth generation it girl."),
]

# ---------------- ACT 1 — CHUNCHEON (~200s) ----------------
BEATS += [
dict(id="a1c", act=1, kind="card", card=dict(kind="chapter",
     num="ACT ONE", title="CHUNCHEON"), refs=[],
     text="Act One. Chuncheon."),
dict(id="a1b01", act=1, kind="clips", tags=["ahyeon"],
     vids=["reveal_ahyeon", "nextmovement"], refs=["F001", "F004"],
     text="Before the pyramids of light and the dome-sized crowds, there is a map dot two hours east of Seoul. Chuncheon — a lakeside city in Gangwon Province, known for its dumplings, its autumn leaves, and almost nothing else in the global music economy. On April 11th, 2007, Jung Ahyeon was born there. By her own fans' accounting she was studying English at five and Mandarin by seven — a trilingual childhood in a city that has produced exactly one global idol."),
dict(id="a1b02", act=1, kind="clips", tags=["ahyeon", "ygent"],
     vids=["nextmovement", "leval1"], refs=["F004", "F002"],
     text="Somewhere between eight and ten years old, she entered the system that would rebuild her life around a single objective. YG Entertainment — the company of BigBang, of 2NE1, of Blackpink — runs the most selective and most secretive training program in K-pop. Trainees practice six to ten hours a day for years without a debut date, without a guarantee, and in most cases without the public ever learning their name. Ahyeon lasted five years in that machine. Hold on to that number. Five years of auditions, evaluations, and eliminations before the outside world saw her face move."),
dict(id="a1b03", act=1, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["nextmovement", "reveal_ahyeon"], refs=["F005"],
     text="The first public signal came on New Year's Day, 2023. A trailer called YG Next Movement — ninety seconds of anonymous trainees dancing like the floor owed them money. The internet did what the internet does: it froze frames, zoomed faces, and started building fan accounts for children whose names had never been spoken. Eleven days later, YG began answering. One by one, it released live performance videos of the members. Ahyeon was the second reveal. She was fifteen years old, performing choreography she had been drilling for half a decade, and the comments read like a launch event."),
dict(id="a1b04", act=1, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["leval1", "reveal_ahyeon"], refs=["F040", "F041"],
     text="Behind the scenes, the selection was being filmed. Last Evaluation — YG's own documentary series — followed seven trainees competing for a lineup no one would guarantee. The footage showed a company deliberately withholding the answer, letting the girls — and the audience — sit inside the uncertainty. Ahyeon made the label's shortlist of five as the complete package — a kid from Chuncheon who sang in English at five, Mandarin at seven, and danced like she'd been on stage since she was five. Not a reference. A first language: music. The question was never whether she fit an old mold, but whether YG was ready to build a new group around a voice that refused to fit one."),
]

# ---------------- ACT 2 — THE VOICE (~195s) ----------------
BEATS += [
dict(id="a2c", act=2, kind="card", card=dict(kind="chapter",
     num="ACT TWO", title="THE VOICE"), refs=[],
     text="Act Two. The voice they heard first."),
dict(id="a2b01", act=2, kind="clips", tags=["ahyeon"],
     vids=["dangerously", "dream"], refs=["F007"],
     text="Here is the detail that separates Ahyeon's origin from every trainee handbook. Before BABYMONSTER had a name, a logo, or a debut date, a video leaked out of the practice rooms: a teenage girl singing Charlie Puth's Dangerously — alone, one take, no stage, no styling. It spread the way genuine things spread, unannounced and unkillable. And then it reached the person who wrote the song. Charlie Puth didn't just notice it. He said publicly that he had heard the cover, and that the voice had stopped him."),
dict(id="a2b02", act=2, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["dream"], refs=["F008"],
     text="On May 14th, 2023, the group released Dream — a pre-debut single that hit number one on Billboard's Hot Trending Songs chart before the group had officially debuted. The YouTube channel crossed one million subscribers in fifty-two days, the fastest in K-pop girl group history at the time. Industry watchers kept asking the same question: why was YG building so much momentum for a group with no release date? The answer, it turned out, was that the date kept moving — because the lineup wasn't finished. One voice was missing."),
dict(id="a2b03", act=2, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["reveal_ahyeon", "leval_ahyeon"], refs=["F004", "F003"],
     text="Inside the company, Ahyeon was being shaped as a specific weapon: main vocalist, lead rapper, lead dancer, center. That is four job descriptions on one person, and each one is normally a full-time specialty. The rare idols who carry all four are the ones the industry builds eras around. YG had a term for what it saw in her — and fans had theirs. Both meant the same thing: the group's identity was designed around a voice that could carry hip-hop swagger on one track and pure pop ache on the next, without changing costumes."),
dict(id="a2b04", act=2, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["dream", "nextmovement"], refs=["F007", "F015"],
     text="The Puth thread didn't end with the cover. Two years later, when the group finally released its first album, track four would be called Like That — written and gifted by Charlie Puth himself, explicitly in response to that practice-room video. Remember the sequence, because it matters: a cover made in anonymity went up the chain, reached the original artist, and came back down as a song on a debut album. In an industry where Western features are bought and negotiated, one of the biggest pop writers on Earth handed a debut track to a trainee he had never met."),
]

# ---------------- ACT 3 — THE WAIT (~250s) ----------------
BEATS += [
dict(id="a3c", act=3, kind="card", card=dict(kind="chapter",
     num="ACT THREE", title="THE WAIT"), refs=[],
     text="Act Three. The wait."),
dict(id="a3b01", act=3, kind="clips", tags=["ahyeon", "ygent"],
     vids=["nextmovement", "leval1"], refs=["F009"],
     text="November 15th, 2023. The notice was three sentences long. YG announced that Ahyeon would not participate in the group's debut activities, citing health and personal circumstances. She would remain a member of BABYMONSTER. No timeline. No diagnosis. No footage. In K-pop, where a nine-month hiatus can quietly end a career, the announcement read like a countdown nobody could see. She was sixteen years old."),
dict(id="a3b02", act=3, kind="clips", tags=["babymonster"],
     vids=["batterup"], refs=["F010"],
     text="Twelve days later, the six-member BABYMONSTER released Batter Up. The numbers were absurd: twenty-two point five nine million views in twenty-four hours — at that moment, the most-viewed debut music video in K-pop history. One hundred million views in eighteen days. The group had arrived, loudly, undeniably — and every article, every comment, every frame of choreography carried the same asterisk. Six of seven. The debut was a triumph shaped exactly like an absence."),
dict(id="a3s", act=3, kind="card", card=dict(kind="stat",
     big="22.59M", small="first-24h views — Batter Up, the most-viewed K-pop debut MV ever, without her"), refs=["F010"],
     text="Twenty-two point five nine million views in the first twenty-four hours."),
dict(id="a3b03", act=3, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["sitm"], refs=["F011"],
     text="February 2024 brought Stuck In The Middle — a ballad-adjacent single that showcased the group's softer register. Again six members. Again the comments. By then, the absence had become the group's most-discussed member. Fan campaigns for her return ran in multiple languages and multiple time zones; the fandom's nickname for the wait — worth the wait — stopped being a slogan and became a prediction. Inside YG, sources say, the decision had already been made. The company did not refilm, did not re-cast, did not re-shuffle. It waited for her."),
dict(id="a3b04", act=3, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["nextmovement", "leval_ahyeon"], refs=["F012"],
     text="In the early spring of 2024, YG posted a notice that fans screenshot like a birth certificate: Ahyeon would rejoin the group. The seven-member rebrand was baked into the identity itself — the debut EP would be stylized BABYMONS7ER, the numeral seven welded into the wordmark. Think about how rare that is. Labels replace members. Labels delay debuts. Labels almost never architect the comeback of a trainee who never debuted into the group's founding mythology. The missing girl was about to become the founding story."),
dict(id="a3x", act=3, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["sheesh"], refs=[],
     text=""),
]

# ---------------- ACT 4 — WORTH THE WAIT (~230s) ----------------
BEATS += [
dict(id="a4c", act=4, kind="card", card=dict(kind="chapter",
     num="ACT FOUR", title="WORTH THE WAIT"), refs=[],
     text="Act Four. Worth the wait."),
dict(id="a4b01", act=4, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["sheesh", "sheesh_facecam"], refs=["F013", "F014"],
     text="April 1st, 2024. Seven members. BABYMONS7ER. The debut EP pulled over four hundred sixty thousand pre-orders and landed at number three on Korea's Circle Album Chart. The title track Sheesh was engineered as a statement — brass stabs, chant hooks, a drop built for stadiums — and it climbed to the top ten of the Circle Digital Chart while posting the highest Spotify debut of any K-pop girl group that year. The center of its choreography, and of nearly every camera move, was the girl who had missed the countdown."),
dict(id="a4b02", act=4, kind="clips", tags=["ahyeon"],
     vids=["sheesh", "likethat"], refs=["F015"],
     text="And there, on the album, sat the full-circle moment: Like That. Written by Charlie Puth. Gifted, by his own account, because a practice-room cover had once stopped him mid-scroll. Ahyeon didn't just get her debut — she got a debut where one of the world's biggest pop writers had personally co-signed the voice the industry spent sixteen months waiting to hear. Critics noticed what YG had bet on: the group's seven-member sound finally had its missing ceiling."),
dict(id="a4b03", act=4, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["interview", "sheesh_stage"], refs=["F016", "F041"],
     text="The press cycle wanted a shortcut — a reference, a familiar frame to explain a new face. Ahyeon didn't give them one. Her answer was never a press release. It was a body of work: a rapper's bite on variety shows, live vocals that kept getting steadier under the harshest open mics, choreography that read clean on a phone screen and even cleaner on a 55,000-seat dome cam. The fifth generation didn't need a repeat. It needed a first — and she was already becoming it, one stage at a time."),
dict(id="a4b04", act=4, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["batterup_stage", "drip_facecam", "sheesh_stage"], refs=["F017"],
     text="The industry's verdict arrived through arithmetic. Within two months of debuting, the group was booked across six Asian territories on a fan-meeting tour, selling twenty-six thousand tickets in Tokyo alone. Music show stages turned into trending clips weekly. The machine that had spent 2019 through 2023 being called too slow, too quiet, too old-fashioned — YG's patient, scarcity-driven training model — had just produced the fastest-scaling girl group of the new generation. And at the center of the frame was the one it had refused to replace."),
]

# ---------------- ACT 5 — MONSTER ERA (~240s) ----------------
BEATS += [
dict(id="a5c", act=5, kind="card", card=dict(kind="chapter",
     num="ACT FIVE", title="MONSTER ERA"), refs=[],
     text="Act Five. The monster era."),
dict(id="a5b01", act=5, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["forever", "drip"], refs=["F018"],
     text="The singles kept the temperature up. Forever, that July, ran the group's bright-powered register into summer. But the real move came on November 1st, 2024: DRIP, the first studio album. Eight hundred twenty thousand copies in its first week — for a group eleven months past debut. It crossed a million domestic copies, landed on the Billboard 200, and its title track carried a co-sign no one saw coming: the demo was built by G-Dragon. The pupil of the company, handed material by its architect."),
dict(id="a5b02", act=5, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["kspo"], refs=["F021", "F022"],
     text="Then came the stat that redrew the tour maps. On January 25th and 26th, 2025, BABYMONSTER opened their Hello Monsters world tour at the KSPO Dome in Seoul — the Olympic gymnastics arena that functions as K-pop's certification of arrival. No girl group had ever headlined that venue faster. They were eight months past debut. The tour went on to play thirty-two shows across twenty cities for roughly three hundred thousand people, with the Japan leg alone moving a hundred and fifty thousand tickets at a record pace."),
dict(id="a5b03", act=5, kind="clips", tags=["ahyeon"],
     vids=["mama_golden"], refs=["F023", "F024"],
     text="November 29th, 2025 — the MAMA Awards in Hong Kong. Ahyeon, Pharita, and Rora took the stage for a medley from KPop Demon Hunters, and their performance of Golden detonated the internet: six point six eight million views, the most-watched MAMA clip of the year. Then came the part every idol learns to dread — the reaction economy. Clips of the live vocals circulated with criticism attached. Ahyeon's response was not a statement. It was the next stage, and the one after that, each one tighter, until the argument ran out of footage."),
dict(id="a5s", act=5, kind="card", card=dict(kind="stat",
     big="6.68M", small="views — the most-watched 2025 MAMA stage (KPop Demon Hunters medley)"), refs=["F023"],
     text="Six point six eight million views — the most-watched MAMA stage of the year."),
dict(id="a5b04", act=5, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["drip", "kspo"], refs=["F022", "F043"],
     text="Zoom out and the year looks like this: a million-copy album, a dome-level world tour, four hundred forty thousand fans through the turnstiles in twelve months, and a fanbase that had watched a sixteen-year-old almost disappear and come back as the group's gravitational center. By the end of 2025, the industry had stopped describing BABYMONSTER as Blackpink's successors. They were simply the monster era — and Ahyeon was its face."),
]

# ---------------- ACT 6 — IT GIRL (~280s) ----------------
BEATS += [
dict(id="a6c", act=6, kind="card", card=dict(kind="chapter",
     num="ACT SIX", title="IT GIRL"), refs=[],
     text="Act Six. The it girl year."),
dict(id="a6b01", act=6, kind="clips", tags=["ahyeon", "babymonster", "airport"],
     vids=["apt_incheon", "icn_2026", "gmp_ot7", "sumersonic"], refs=["F026", "F025"],
     text="By 2026, the metric wasn't views anymore. It was what happened when there was no stage at all. August 19th, 2024 — 11:30 at night, Incheon, solo, no bodyguards, a rookie five months after debut. The amount of cameras and people for one Ahyeon was insane — hundreds deep, phones up, gifts out. She almost disappeared into it, then steadied — waving, thanking, stopping when someone got pushed. It happened four more times — Gimpo as seven, Haneda in Japan, September 2026 in a white long-sleeve making a heart with her fingers while a crowd shouted don't get hurt. The industry has a word for that. They call it an it girl."),
dict(id="a6b02", act=6, kind="clips", tags=["ahyeon"],
     vids=["choom"], refs=["F027", "F028"],
     text="March brought the fashion system's stamp: a Vogue Hong Kong cover. April brought the fans' stamp: at the Korean Global Music Awards, she took Artist of the April — a solo-female category — with thirty-three thousand three hundred eighty votes, eighty-five point eight percent of the entire ballot. That is not a win; that is a monopoly. And she turned nineteen that month, which means the it girl conversation was happening about a teenager who was still, in industry terms, at the beginning."),
dict(id="a6b03", act=6, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["choom", "choom_stage"], refs=["F031", "F032"],
     text="May 4th — third mini album, CHOOM: a record built for movement, and a title-track move so clean it escaped the song entirely. The Ahyeon March — her shoulder-led strut from the challenge video — went viral on TikTok, Douyin, and Xiaohongshu, remixed by dancers who had never streamed a BABYMONSTER track in their lives. That is the it girl signature: when your choreography becomes infrastructure. When the culture takes one piece of you and runs without asking."),
dict(id="a6b04", act=6, kind="clips", tags=["babymonster", "ahyeon"],
     vids=["shit"], refs=["F033", "F034"],
     text="June's SUGAR HONEY ICE TEA hit number one on YouTube's global daily music chart and blew past a hundred million views. In July, CHOOM debuted at number thirty-five on US Mediabase Top Forty — the group's first American radio entry, a wall that has stopped bigger acts cold. And on September 3rd, the channel crossed ten billion cumulative views: the fastest K-pop girl group ever to get there, the second in history after Blackpink. The company's slow-cooked model now had a number the whole industry could read."),
dict(id="a6s", act=6, kind="card", card=dict(kind="stat",
     big="10,000,000,000", small="cumulative channel views — fastest K-pop girl group ever (Sep 3, 2026)"), refs=["F035"],
     text="Ten billion cumulative views — faster than any girl group in history."),
dict(id="a6b05", act=6, kind="clips", tags=["ahyeon"],
     vids=["interview", "choom"], refs=["F036", "F038"],
     text="September's award season produced the clip that tells the whole story. At an international music awards show in Hong Kong, Ahyeon walked up for a group honor and delivered the acceptance speech entirely in Mandarin — fluent, unhurried, ending with a line fans translated and re-translated across every platform: I would give my whole world to you. By then the fan archives had a name for the year. Not the comeback. Not the victory tour. The it girl year — a phrase that used to belong to whoever magazines chose, now anchored to someone the internet chose first."),
]

# ---------------- ACT 7 — THE CRAFT (~195s) ----------------
BEATS += [
dict(id="a7c", act=7, kind="card", card=dict(kind="chapter",
     num="ACT SEVEN", title="THE CRAFT"), refs=[],
     text="Act Seven. Why she lands."),
dict(id="a7b01", act=7, kind="clips", tags=["ahyeon"],
     vids=["sheesh_stage", "choom_stage"], refs=["F003", "F039"],
     text="Strip the narrative away and what remains is technique. The voice: a bright, cut-through register with a rapper's sense of rhythm underneath it — the reason she can pivot from a sung hook to a verse without the song changing shape. On the CHOOM tour's Seoul dates, her solo cover of Ariana Grande's Problem was reported as the loudest turn of the night — a whistle-adjacent vocal stunt that most twenty-year-old idols wouldn't attempt in a practice room, performed by a nineteen-year-old in front of a home crowd."),
dict(id="a7b02", act=7, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["mama_golden", "kspo"], refs=["F024", "F023"],
     text="The comeback after MAMA is the part the highlight reels skip. Live-vocal criticism in K-pop is not a news cycle; it is a permanent search result. The only working answer is repetition in public — more stages, steadier takes, no hiding behind backing tracks. Watch the arc from that November night through the dome concerts ten months later and you can hear the difference in real time: tighter breath control, cleaner pitch under choreography, a performer who stopped treating the camera as a witness and started treating it as an instrument."),
dict(id="a7b03", act=7, kind="clips", tags=["ahyeon"],
     vids=["interview", "reveal_ahyeon"], refs=["F038", "F001"],
     text="And then the layer almost nobody gets: language. Korean for the members and the fans at home. English from age five — the interviews, the global press, the Vogue sit-downs. Mandarin from age seven — Taipei, Macau, Hong Kong, Kai Tak. Three audiences, three registers, one person. The it girl label usually describes an aesthetic. Hers is logistics: the ability to be understood in three economies without a translator, and to make each crowd feel like the show was mounted for them alone."),
]

# ---------------- ACT 8 — THE DOME (~250s) ----------------
BEATS += [
dict(id="a8c", act=8, kind="card", card=dict(kind="chapter",
     num="ACT EIGHT", title="THE DOME"), refs=[],
     text="Act Eight. The dome."),
dict(id="a8b01", act=8, kind="clips", tags=["babymonster", "ahyeon", "crowd"],
     vids=["kyocera_hype", "sumersonic"], refs=["F037", "F042"],
     text="September 22nd and 23rd, 2026 — Kyocera Dome, Osaka — fifty-five thousand seats, BABYMONSTER's first solo dome concerts. The film closes the loop it opened: the girl left behind in a building full of mirrors, and the vocabulary that changed around her."),
dict(id="a8b02", act=8, kind="clips", tags=["ahyeon", "crowd"],
     vids=["kyocera_hype", "taipei_moment", "sumersonic", "soundcheck"], refs=["F029", "F035"],
     text="But the moment that mattered happened outside the dome too — in Taipei, on a flower cart during SUPA DUPA LUV and Love In My Heart, running to the edge to close the gap. And in Osaka, hyping a crowd to sing along until the dome itself sang back."),
dict(id="a8b03", act=8, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["choom", "shit", "sheesh"], refs=["F037"],
     text="So here is the answer to the question the title keeps asking. An it girl is not made by a magazine cover, a viral march, or ten billion views — those are receipts, not reasons. Jung Ahyeon is the fifth generation's it girl because she is the rarest thing the system can produce: a center who was removable, who wasn't removed, and who came back indispensable. The debut happened without her. The era happened because of her. And whatever comes next — the encore tours, the solo era the fans already campaign for, the second dome — the industry will be watching the same way it has watched her since a practice-room cover leaked: unable to look away, and unable to explain why the girl from Chuncheon keeps doing the impossible quietly, in three languages, at nineteen."),
dict(id="a8x", act=8, kind="clips", tags=["ahyeon", "babymonster"],
     vids=["dome_fancam"], refs=[],
     text=""),
dict(id="a9close", act=8, kind="card", card=dict(kind="close",
     lines=["THE DEBUT HAPPENED WITHOUT HER.", "THE ERA HAPPENED BECAUSE OF HER.", "AHYEON — WORTH THE WAIT."]), refs=["F009", "F013"],
     text="The debut happened without her. The era happened because of her."),
dict(id="a9cred", act=8, kind="card", card=dict(kind="credits",
     lines=["AHYEON — THE 5TH GEN IT GIRL",
            "FACTS: WIKIPEDIA · YG NOTICE · BILLBOARD · CHOSUN · KOREA HERALD",
            "VOGUE HONG KONG · KGMA · MEDIABASE · MAMA 2025",
            "FOOTAGE: BABYMONSTER OFFICIAL CHANNELS",
            "MUSIC: ORIGINAL SCORE — CC0 SAMPLES",
            "PIANO: SALAMANDER GRAND PIANO V3 (CC BY 3.0)",
            "PRODUCED WITH LAST STOP YT ENGINE",
            "FAN-MADE DOCUMENTARY · NOT AFFILIATED WITH YG"], refs=[]),
     text=""),
]
