#!/usr/bin/env python3
"""script_beats.py — narration script for 'Why there will be no next BLACKPINK'
Target: 34:00 (2040s) · fact-gated to research/facts.json (refs per beat)
Beat kinds: clips (montage pool) | card (typographic overlay over looping clip)
Every text block = one narration paragraph = one TTS run.
"""
BEATS = []

# ---------------- ACT 0 — COLD OPEN (~95s, ~230w) ----------------
BEATS += [
dict(id="co1", act=0, kind="clips", tags=["blackpink"],
     vids=["IHNzOHi8sJs","2S24-y0Ij3Y","ioNng23DkIM"], refs=["F001","F080"],
     text="On August 8th, 2016, two music videos went up on YouTube at the same hour. One girl group. One company that had not launched a girl group in seven years. Within a decade, that group would hold the most-subscribed artist channel in the platform's history, the highest-grossing tour by any female group ever, and more than forty billion streams. And then — the releases slowed to a trickle. Three and a half years between albums. Four women building solo empires bigger than their own group. This is not the story of a band on hiatus. This is the anatomy of a machine that ran once — and cannot run again."),
dict(id="co2", act=0, kind="card", card=dict(kind="title",
     lines=["WHY THERE WILL BE","NO NEXT BLACKPINK"]), refs=["F001"],
     text="Why there will be no next Blackpink."),
]

# ---------------- ACT 1 — THE VACUUM (~260s, ~630w) ----------------
BEATS += [
dict(id="a1c", act=1, kind="card", card=dict(kind="chapter",
     num="ACT ONE", title="THE VACUUM"), refs=[],
     text="Act One. The vacuum."),
dict(id="a1b01", act=1, kind="clips", tags=["ygent","industry"],
     vids=["2wA_b6YHjqQ","VdhLxKFcOWQ"], refs=["F002","F009"],
     text="To understand why Blackpink is unreproducible, you have to start with a hole. In 2011, YG Entertainment pencilled in plans for a new girl group. And then nothing happened. For five years. In an industry that debuts dozens of girl groups a season, seven years passed between YG's 2NE1 and Blackpink's first single. That gap was not indecision. It was a filter."),
dict(id="a1b02", act=1, kind="clips", tags=["jennie","ygent"],
     vids=["HFQBxmv0GWc","7jx_vdvxWu0"], refs=["F005","F074"],
     text="The filter processed exactly four survivors. Jennie Kim — sent to New Zealand at eight years old, schooled in English and distance, walking back into Seoul in 2010 to audition for the company that had watched her leave. Six years as a trainee before the world heard her name. YG called her their secret weapon for so long that the secret became the marketing."),
dict(id="a1b03", act=1, kind="clips", tags=["jisoo","blackpink"],
     vids=["73ZA1phZIeM","7jx_vdvxWu0"], refs=["F006","F073"],
     text="Kim Jisoo joined in July 2011 — five years of training ahead of her, years spent singing for visitors at company showcases while older groups got the comebacks. She would become the group's lead vocalist and, eventually, a Dior and Cartier ambassador whose solo album would outsell every Korean female soloist before her. But in 2011, she was a teenager with no debut date."),
dict(id="a1b04", act=1, kind="clips", tags=["rose"],
     vids=["62VN_HFBA48","WWvxT6ttDE0"], refs=["F007","F075"],
     text="Rosé — Roseanne Park — was a schoolgirl in Melbourne when YG held a 2012 audition in Australia. Seven hundred applicants. She ranked first. Her family drove her to the airport; at fifteen she landed in a country where she knew the company and nobody else. Four years of training. On late-night American television, years later, she still tells the story like someone describing a coin flip that decided her life."),
dict(id="a1b05", act=1, kind="clips", tags=["lisa"],
     vids=["8trQcKnh9X8","UxXY_hR_wzo"], refs=["F008","F076"],
     text="And Lalisa Manobal — Pranpriya, the beloved — a dancer from Buriram, Thailand, who flew herself into a 2010 YG audition in Bangkok. Four thousand applicants. She was the only one passed. She moved to Korea at thirteen, alone, not speaking the language, and trained for five years. Four girls. Two auditions with a survival rate of one in four thousand. Nearly two decades of combined training before a single frame of content existed. Hold on to that number. Because it is the first reason there will be no next Blackpink: the machine that found them no longer exists."),
dict(id="a1b06", act=1, kind="clips", tags=["2ne1"],
     vids=["j7_lSP8Vc3o","vLbfv-AAyvQ","_Sm_BIkbJkw"], refs=["F010","F064","F068"],
     text="The room they were built to fill had a shape, and the shape came from 2NE1. YG's first girl group debuted in 2009 and within two years swept all three major year-end artist prizes in Korea — a feat no act had managed that fast. They sold over sixty-six million records. They proved a Korean girl group could be fierce, hip-hop-forward, globally credible — none of the innocence, all of the swagger. Blackpink was drafted, from day one, as the answer to the hole 2NE1 would leave."),
dict(id="a1b07", act=1, kind="clips", tags=["2ne1"],
     vids=["vLbfv-AAyvQ","_Sm_BIkbJkw"], refs=["F010","F011"],
     text="And then the hole arrived early. November 25th, 2016 — three and a half months after Blackpink's debut — YG formally disbanded 2NE1. The members learned about it in the news. Minzy had already left that spring; the others were told, in effect, by press release. Years later, two of them confirmed on camera that no one had informed them beforehand. The fans never forgave it. And YG — sitting on the most valuable girl group brand in K-pop history — learned its own lesson in the cruellest possible way: scarcity is not free. Someone always pays for the pause."),
]

# ---------------- ACT 2 — SQUARE ONE (~270s, ~655w) ----------------
BEATS += [
dict(id="a2c", act=2, kind="card", card=dict(kind="chapter",
     num="ACT TWO", title="SQUARE ONE"), refs=[],
     text="Act Two. Square One."),
dict(id="a2b01", act=2, kind="clips", tags=["blackpink"],
     vids=["bwmSjveL3Lc","IHNzOHi8sJs"], refs=["F001","F002"],
     text="August 8th, 2016. SQUARE ONE. Two songs, no album — YG releasing music the way a jeweller releases stones: one at a time, at premium prices. The first was Boombayah. The second was Whistle. Together they announced a design philosophy that ran against everything the industry believed in 2016."),
dict(id="a2b02", act=2, kind="clips", tags=["blackpink"],
     vids=["IHNzOHi8sJs","bwmSjveL3Lc"], refs=["F003","F004"],
     text="Whistle went to number one on Korea's Gaon Digital Chart. Boombayah took number one on Billboard's World Digital Songs. Their fandom name arrived like a signature: BLINK. And then, immediately, the group went quiet again. One single album. Months of nothing. In an ecosystem where a new group's survival depended on constant broadcasts, variety shows, and weekly promotions, YG starved its own debut act on purpose."),
dict(id="a2b03", act=2, kind="clips", tags=["blackpink","jennie","lisa","rose","jisoo"],
     vids=["bwmSjveL3Lc","2S24-y0Ij3Y","ioNng23DkIM"], refs=["F002","F009"],
     text="The logic only makes sense from above. Blackpink debuted after the streaming shift, after YouTube had replaced music shows as the global stage — so broadcast saturation was irrelevant. What mattered was the frame: four faces, each one a luxury billboard, each frame composed like an advertisement. The scarcity wasn't neglect. It was pricing. A group that releases rarely can only afford to be seen as premium. YG turned absence into brand equity — and it worked, because the audience was new, the format was new, and no one else was doing it."),
dict(id="a2b04", act=2, kind="clips", tags=["blackpink"],
     vids=["2S24-y0Ij3Y","gQlMMD8auMs","9pdj4iJD08s"], refs=["F013"],
     text="SQUARE TWO. Playing With Fire. Stay. Then As If It's Your Last — and then, in June 2018, Square Up. DDU-DU DDU-DU debuted at number 55 on the Billboard Hot 100 — at that moment the highest entry ever for a Korean girl group, a number that would look quaint within eighteen months. The Korean music industry began using a new word for what was happening: Blackpink was going global without going to the West first. The West was coming to them."),
dict(id="a2b05", act=2, kind="clips", tags=["blackpink"],
     vids=["9pdj4iJD08s","Amq-qlqbjYA","FzVR_fymZw4"], refs=["F009"],
     text="Look at the timeline again: the plans date to November 2011. The name is confirmed June 29th, 2016. Five years of silence between intention and debut — while the members trained, while the industry moved on, while every competitor debuted faster and younger. When the group finally arrived, it arrived pre-mythologised. There was no next Blackpink even then. There was only the one, engineered in a vacuum nobody else had the patience — or the ruthlessness — to create."),
]

# ---------------- ACT 3 — THE RECORD MACHINE (~330s, ~740w) ----------------
BEATS += [
dict(id="a3c", act=3, kind="card", card=dict(kind="chapter",
     num="ACT THREE", title="THE RECORD MACHINE"), refs=[],
     text="Act Three. The record machine."),
dict(id="a3b01", act=3, kind="clips", tags=["blackpink"],
     vids=["POe9SOEKotk","IHNzOHi8sJs"], refs=["F013","F014"],
     text="What followed Square Up was less a discography than a sequence of detonations. DDU-DU DDU-DU went to number one on Gaon, and its video — thirty-six million views in the first twenty-four hours — became the first K-pop group video ever to pass a billion views. Then two billion. The pistol-finger choreography became the most-recognised three seconds in modern K-pop, imitated from Seoul to Sao Paulo by people who could not name a single other Korean song."),
dict(id="a3b02", act=3, kind="clips", tags=["blackpink"],
     vids=["2S24-y0Ij3Y","RkKXbweBCcI"], refs=["F015","F016"],
     text="Kill This Love premiered with fifty-six point seven million first-day views — at the time, the biggest debut in YouTube's history, any artist, any genre. A year later, How You Like That broke five Guinness World Records in a single day, including the largest premiere audience ever assembled online: one point six six million people watching simultaneously, at four in the morning in half the world's time zones. It won Song of Summer at the VMAs — the first Korean female act to take a Moonman home."),
dict(id="a3b03", act=3, kind="clips", tags=["blackpink"],
     vids=["gQlMMD8auMs","dyRsYk0LyA8"], refs=["F018","F019"],
     text="The albums compounded like interest. The Album, October 2020: the first million-selling album by a K-pop girl group, and the first girl group of any nationality to top Billboard's Artist 100. Born Pink, September 2022: first K-pop girl group past two million copies, first album by a female Korean act to hit number one on the Billboard 200, first K-pop girl group to top the UK — the first girl group to own America and Britain at the same time since the Spice Girls in 2001."),
dict(id="a3b04", act=3, kind="clips", tags=["blackpink"],
     vids=["VLpUsmBafMQ","a5gUds01aXY"], refs=["F020","F021","F022","F023"],
     text="And the audience kept compounding. Guinness certified them the most-subscribed band on YouTube in 2021 — then the most-subscribed music act on the planet, period. By 2026 they became the first artist in history to cross one hundred million subscribers, earning a custom Red Diamond award YouTube had to invent. Forty-one point seven five billion lifetime views. Sixteen point nine billion Spotify streams — the most-streamed female group ever recorded. Twenty million records. These are not K-pop records. They are platform records that happen to be held by four women from Seoul."),
dict(id="a3b05", act=3, kind="clips", tags=["blackpink"],
     vids=["cxNIewNXpcg","3l5jwqPT2yk"], refs=["F024","F025","F026"],
     text="Then the tours turned the machine into a money furnace. The Born Pink World Tour: one point eight million tickets, the most-attended tour by any Korean girl group in history, three hundred and thirty million dollars grossed — past the Spice Girls' record, past every Asian act in history. Coachella 2023: the first Asian act ever to headline the festival, four years after becoming the first female K-pop group to play it at all. In the desert that night, the crowd sang the Korean bridge of every song back at the stage."),
dict(id="a3b06", act=3, kind="clips", tags=["blackpink"],
     vids=["2S24-y0Ij3Y","dyRsYk0LyA8"], refs=["F027","F028","F029","F083"],
     text="And even the comeback after the three-and-a-half-year silence broke form: the Deadline World Tour opened at Goyang Stadium and rolled through London's Wembley — the first K-pop girl group to headline that building. A new single, Jump, released outside the American label system for the first time since 2018, distributed through the Orchard, and it still became their third number one on Billboard's Global 200 — the most by any female act. The machine, restarted after years idle, did not sputter. It broke its own records within a week."),
]

BEATS += [
dict(id="i1", act=3, kind="clips", tags=["blackpink"],
     vids=["VLpUsmBafMQ","a5gUds01aXY","cxNIewNXpcg","RkKXbweBCcI"], refs=[], text=""),
]

# ---------------- ACT 4 — THE MACHINE THAT BUILT THEM (~300s, ~700w) ----------------
BEATS += [
dict(id="a4c", act=4, kind="card", card=dict(kind="chapter",
     num="ACT FOUR", title="THE MACHINE THAT BUILT THEM"), refs=[],
     text="Act Four. The machine that built them."),
dict(id="a4b01", act=4, kind="clips", tags=["blackpink","ygent"],
     vids=["7jx_vdvxWu0","befa9vOsQFk"], refs=["F012"],
     text="Here is the number that explains the whole strategy: in their first nine years, Blackpink released roughly thirty songs. Thirty. Their peers in the same industry released a hundred or more in the same window — multiple albums a year, Japanese editions, winter singles, sub-units. YG chose the opposite path and defended it for a decade: fewer releases, each one an event, each one dressed like luxury, priced like luxury, framed like luxury. Scarcity wasn't a side effect. It was the product."),
dict(id="a4b02", act=4, kind="clips", tags=["blackpink"],
     vids=["POe9SOEKotk","9pdj4iJD08s","gQlMMD8auMs"], refs=["F074","F075","F076","F073"],
     text="The luxury was literal. Jennie became Chanel's human embodiment — front row, campaigns, custom looks, the industry nickname stuck: Human Chanel. Rosé anchored Saint Laurent and YSL Beauty. Lisa held Celine and Bulgari simultaneously. Jisoo carried Dior and later Cartier. Four members, four global fashion houses, no overlap, no cannibalisation. No K-pop group — no pop group of any origin — has ever carried that concentration of fashion capital at once."),
dict(id="a4b03", act=4, kind="clips", tags=["blackpink"],
     vids=["HFQBxmv0GWc","73ZA1phZIeM"], refs=["F069","F070","F071"],
     text="The reach followed. Four hundred and twelve million combined Instagram followers by 2025 — the four most-followed individuals based in South Korea, each one of them individually bigger on that platform than their own group's official account. Time magazine named them Entertainer of the Year for 2022. King Charles the Third made all four honorary Members of the Order of the British Empire. Think about the arc: four girls who could not get a broadcast slot in Korea in 2015 were being decorated at Buckingham Palace eight years later."),
dict(id="a4b04", act=4, kind="clips", tags=["blackpink"],
     vids=["IHNzOHi8sJs","2S24-y0Ij3Y","ioNng23DkIM"], refs=["F077"],
     text="Underneath the glamour, the engineering held. Four positions, deliberately built: Jennie the main rapper with lead-vocal range, Lisa the main dancer with rap presence, Rosé the main vocalist with the signature timbre, Jisoo the lead vocalist with acting gravity. Two rappers, two vocalists, two foreign-born members, four languages between them, four distinct brand identities. The group was designed so that every single member could, in theory, carry a solo career alone — an insurance policy that would later become the exit ramp."),
dict(id="a4b05", act=4, kind="clips", tags=["ygent","industry"],
     vids=["2wA_b6YHjqQ","VdhLxKFcOWQ"], refs=["F061","F062"],
     text="Which raises the obvious question: if the model worked so well, why hasn't it been repeated? YG tried. BABYMONSTER — seven members, debuted November 2023 with the same scarcity logic, the same producer bench, the same marketing playbook. Their album sold a million copies and they headlined Seoul's Olympic arena faster than any female act in history. And yet the press coverage kept comparing them, unfavourably, to the group they were built to replace; industry insiders had ranked them ninth in pre-debut anticipation. The formula was public. The vacuum was not. You cannot schedule lightning."),
]

# ---------------- ACT 5 — THE CONTRACT CLIFF (~300s, ~700w) ----------------
BEATS += [
dict(id="a5c", act=5, kind="card", card=dict(kind="chapter",
     num="ACT FIVE", title="THE CONTRACT CLIFF"), refs=[],
     text="Act Five. The contract cliff."),
dict(id="a5b01", act=5, kind="clips", tags=["blackpink"],
     vids=["befa9vOsQFk","2kuOJtPgHLE"], refs=["F053","F054"],
     text="Every K-pop group lives inside a seven-year clock. For Blackpink, that clock struck August 2023 — the standard contract term expiring for all four members at once, seven years to the month after SQUARE ONE. The industry held its breath. Analysts priced the scenarios. YG's stock tracked every rumour. July came: negotiations ongoing. November came: negotiations ongoing. The most valuable girl group in history sat, unsigned, for the back half of its own anniversary year."),
dict(id="a5b02", act=5, kind="clips", tags=["blackpink"],
     vids=["2kuOJtPgHLE","W7f-6dVvw7I"], refs=["F054","F055"],
     text="December 5th, 2023: the announcement. All four members renewed — for group activities. YG promised a new album and a world tour. Fans exhaled. And then, three weeks later, on December 29th, the second half of the statement landed, and it was the sentence that mattered: the members did not renew their individual contracts with YG. Solo activities would be handled independently. The group stayed. The four women, as individual businesses, walked."),
dict(id="a5b03", act=5, kind="clips", tags=["jennie","jisoo","lisa","rose"],
     vids=["b73BI9eUkjM","ekr2nIex040","dNCWe_6HAM8","YudHcBIxlYw"], refs=["F033","F038","F044","F050"],
     text="Look at what they walked into. Jennie incorporated her own label — Odd Atelier. Lisa announced LLOUD, her own management company. Jisoo had already registered Blissoo. Rosé signed with The Black Label and, for the West, Atlantic Records. Within one December, four separate corporate entities replaced a single line in a YG ledger. From 2024 onward, the group was a joint venture — four independent companies agreeing to meet — instead of four employees on salary."),
dict(id="a5b04", act=5, kind="clips", tags=["blackpink"],
     vids=["7dP07oQSiUA","VLpUsmBafMQ"], refs=["F056","F057","F058"],
     text="The economics of that flip are brutal. In the old structure, every solo album, every campaign, every acting role paid the house. In the new one, the house gets a slice of only what happens under its roof — and the members' solo businesses promptly outgrew the group's output. 2024 proved it: a full year with no group music, just a cinema release and one fan event, while all four solo careers ran hot. When YG's founder confirmed a 2025 comeback, it read less like a plan and more like a negotiation."),
dict(id="a5b05", act=5, kind="clips", tags=["2ne1","blackpink"],
     vids=["_Sm_BIkbJkw","j7_lSP8Vc3o"], refs=["F010","F011","F065","F066","F068"],
     text="And the precedent that haunts every negotiation is the same one that opened this film. 2NE1 — disbanded by press release, members finding out from the news, a fandom that never came back to the company. Years later, a surprise reunion at Coachella proved the demand was still there: sixty-six million records sold, and a crowd that screamed every word a decade on. The lesson YG learned — too late, publicly, expensively — was that breaking trust with the four women who ARE the asset is the one unrecoverable error. In 2023, on the other side of that history, nobody at the table could afford to be the executive who lost Blackpink. And nobody on the other side of the table needed to fear walking away."),
]

# ---------------- ACT 6 — SOLO GRAVITY (~330s, ~760w) ----------------
BEATS += [
dict(id="a6c", act=6, kind="card", card=dict(kind="chapter",
     num="ACT SIX", title="SOLO GRAVITY"), refs=[],
     text="Act Six. Solo gravity."),
dict(id="a6b01", act=6, kind="clips", tags=["jennie"],
     vids=["b73BI9eUkjM","bB3-CUMERIU"], refs=["F031","F033","F034"],
     text="Start with the proof of concept. SOLO — Jennie, 2018, recorded almost as a side project. It topped every Korean chart and Billboard's world songs list, and its video became the first by any Korean female soloist to cross a billion views. A decade later came You and Me, her first number one on Billboard's global chart outside America. Then Ruby — March 2025: a million copies in a week, number three on the UK album chart, the highest placement by a K-pop female soloist at the time, three songs on the Hot 100 simultaneously — another first. Add HBO's The Idol, where her screen presence outlived the show's reputation. Jennie Kim does not need Blackpink. The numbers settled that argument."),
dict(id="a6b02", act=6, kind="clips", tags=["lisa"],
     vids=["awkkyBH2zEo","dNCWe_6HAM8"], refs=["F036","F037","F039"],
     text="Lisa might need it least. LALISA, 2021: seven hundred and thirty-six thousand copies in a week — the biggest debut week ever recorded by a female artist in Korea. MONEY became the first track by any K-pop soloist to reach a billion streams on Spotify — her eighth Guinness World Record by age twenty-six. Then she left the structure entirely: Rockstar, released through her own LLOUD with RCA, a TikTok record for a million followers in under three hours, New Woman with Rosalía. The girl from the four-thousand-to-one audition became the most-followed K-pop artist on Earth."),
dict(id="a6b03", act=6, kind="clips", tags=["lisa"],
     vids=["hbcGx4MGUMg","UxXY_hR_wzo"], refs=["F040","F041","F042"],
     text="Alter Ego, February 2025: top ten on the Billboard 200, number one album sales in America. An acting debut in The White Lotus — HBO's flagship — as herself-cast, not as a stunt. One hundred and six million Instagram followers. When the group pauses, Lisa's calendar does not. That is the entire structural problem in one sentence."),
dict(id="a6b04", act=6, kind="clips", tags=["rose"],
     vids=["CKZvWhCqx1s","K9_VFxzCuQ0"], refs=["F043","F044"],
     text="Rosé's solo story wrote the blueprint early. -R-, March 2021: four hundred and forty-eight thousand first-week copies — a record for a Korean female soloist — and On the Ground made her the first artist ever to top Billboard's Global 200 as both a group member and a soloist. Then came the Atlantic deal, and with it, the song that swallowed the industry whole."),
dict(id="a6b05", act=6, kind="clips", tags=["rose"],
     vids=["ekr2nIex040","eA0lHNZ1KCA"], refs=["F045","F046","F047","F048","F079"],
     text="APT. — Rosé and Bruno Mars, October 2024. Number eight on the Hot 100 in its first week, peak of number three. Number two in Britain. Number ones in Canada, Australia, New Zealand, a perfect all-kill at home. A billion YouTube views in a hundred and five days. And then the industry awards began falling: IFPI's best-selling single on the planet for 2025 — the first artist from outside Europe and North America to ever top that chart — the first VMA Song of the Year for any K-pop act, three Grammy nominations, the most for any Korean artist in history. Roughly two point seven billion views and counting. Not a Blackpink song. A side project."),
dict(id="a6b06", act=6, kind="clips", tags=["jisoo"],
     vids=["YudHcBIxlYw","NuxAOC6RU9c","2V6lvCUPT8I"], refs=["F049","F050","F051","F052"],
     text="And Jisoo — the one the industry once called the weakest card — quietly won the streaming era. ME, March 2023: the first album by a Korean female soloist to sell a million copies, Flower at number two on the global chart, records in Canada and Britain. Snowdrop put her on Disney Plus in launch markets worldwide. Amortage followed in 2025, then a Netflix series, then a single, Click, teasing her first full album — released on her own Blissoo label. Four members. Four solo empires. Four independent companies. The group was the launchpad — and every rocket left the pad."),
]

BEATS += [
dict(id="i2", act=6, kind="clips", tags=["jennie","lisa","rose","jisoo"],
     vids=["b73BI9eUkjM","awkkyBH2zEo","ekr2nIex040","YudHcBIxlYw"], refs=[], text=""),
]

# ---------------- ACT 7 — WHY NO NEXT (~260s, ~620w) ----------------
BEATS += [
dict(id="a7c", act=7, kind="card", card=dict(kind="chapter",
     num="ACT SEVEN", title="WHY THERE WILL BE NO NEXT"), refs=[],
     text="Act Seven. Why there will be no next."),
dict(id="a7b01", act=7, kind="card", card=dict(kind="stat",
     big="1 IN 4,000", small="LISA'S AUDITION · YG THAILAND 2010"), refs=["F008"],
     text="Reason one: the vacuum. Blackpink was built in a window that closed behind them — a seven-year company gap, four thousand-to-one audition filters, half a decade of silent training, and a global audience with no other Korean option. Every company now debuts acts into a saturated market where that patience looks like malpractice. The conditions were an accident of timing. Timing does not repeat on request."),
dict(id="a7b02", act=7, kind="card", card=dict(kind="stat",
     big="~30 SONGS", small="NINE YEARS · THE SCARCITY MODEL"), refs=["F012"],
     text="Reason two: the model ate itself. Scarcity worked because each release was an event — but events require absence, and absence is only bearable when the audience trusts the return. Blackpink could survive three-and-a-half-year gaps because they were Blackpink. A new group attempting the same strategy dies in month six. And the streaming era has punished every label that tried it. The playbook is now unrepeatable by design."),
dict(id="a7b03", act=7, kind="clips", tags=["jennie","lisa","rose","jisoo"],
     vids=["bB3-CUMERIU","hbcGx4MGUMg","ekr2nIex040","2V6lvCUPT8I"], refs=["F055","F056","F069"],
     text="Reason three — the one that settles it permanently: the economics inverted. On December 29th, 2023, the individual became the primary asset and the group became the side project. Four hundred million followers, four fashion houses, four independent labels, a three-Grammy side project. No agency will ever again sign four future solo superstars onto one contract and one seven-year clock — because now everyone can do the arithmetic of what that costs. The next group will be built solo-first, contractually solo-forever. The machine that made Blackpink required four women whose value was locked inside the group. That lock no longer exists — anywhere."),
dict(id="a7b04", act=7, kind="clips", tags=["ygent","industry","blackpink"],
     vids=["2wA_b6YHjqQ","VdhLxKFcOWQ","POe9SOEKotk"], refs=["F061","F062","F072"],
     text="And reason four: the successors all flinch. YG's own BABYMONSTER — the closest thing to a replay — debuted to a million-selling album and an industry ranking of ninth. NewJeans, Aespa, IVE moved the domestic market without moving the Western stadium economics an inch. The industry keeps building girl groups. None of them can assemble the one ingredient that made this work: an audience that had nowhere else to look. Everyone looks everywhere now. That was the last time the whole world watched one stage at once."),
dict(id="a7b05", act=7, kind="clips", tags=["blackpink"],
     vids=["dyRsYk0LyA8","2S24-y0Ij3Y"], refs=["F030","F059","F060"],
     text="Epilogue, February 2026. The first full-group album in three and a half years — Deadline — sold one point four six million copies on its first day, the biggest first day ever recorded by a K-pop girl group. The demand never died. It just stopped requiring the group. Six months earlier, on the tenth anniversary of their debut, the celebration offered to fans was a meet-and-greet for forty people at a museum — and four women apologising for the scale of their own anniversary. That is the whole story in one image: the machine still counting the money, no longer able to build the room."),
]

# ---------------- ACT 8 — CLOSE (~95s, ~215w) ----------------
BEATS += [
dict(id="a8b01", act=8, kind="clips", tags=["blackpink"],
     vids=["IHNzOHi8sJs","VLpUsmBafMQ","ekr2nIex040"], refs=["F001","F021","F023"],
     text="So no — there will be no next Blackpink. Not because they failed. Because they succeeded past the point where the structure could hold them. Four girls out of four thousand applicants walked into a vacuum, and by the time the vacuum refilled with imitators, they were no longer in it. The group was never the destination. It was the launch sequence."),
dict(id="a8b02", act=8, kind="card", card=dict(kind="close",
     lines=["THE MACHINE RAN ONCE.","MACHINES LIKE THAT","DO NOT RUN TWICE."]),
     refs=[], text="The machine ran once. Machines like that do not run twice."),
dict(id="a8b03", act=8, kind="card", card=dict(kind="credits",
     lines=["A LAST STOP YT ENGINE PRODUCTION","SOURCES: VERIFIED LEDGER — 83 FACTS",
            "FOOTAGE: OFFICIAL BROADCASTS & MUSIC VIDEOS","RESEARCH: R-BLACKPINK DOSSIER 2026"]),
     refs=[], text=""),
]
