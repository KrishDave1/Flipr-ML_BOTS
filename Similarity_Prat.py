import sys
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

sys.stdout.reconfigure(encoding='utf-8')

model = SentenceTransformer('all-MiniLM-L6-v2')

nlp = spacy.load("en_core_web_sm")

articles = [
     """India was one of the top nations in badminton only a few years ago, with players like PV Sindhu and Saina Nehwal securing golds year after year at multiple events, including the Olympics. However, over the past couple of years, India has failed to secure any major title, including a medal at the 2024 Paris Olympics. The downfall started when ace Indian shuttler PV Sindhu suffered an injury two years ago and has since struggled to regain her peak level after returning to the court in 2024. India has a long history of players picking up the baton from former greats — Sindhu herself replaced Nehwal as the country's top player. But now, the issue is that there is no pipeline of world-beating shuttlers after Sindhu. The results from the start of this year’s events highlight the trouble India now finds itself in. Disappointing start to the season
 
The 2025 season has begun on a disappointing note for Indian badminton, raising concerns about the country's overall depth in the sport. At the Badminton Asia Mixed Team Championship (BAMTC), India, despite fielding a strong squad, was eliminated in the quarterfinals against an underpowered Japan. Similarly, at the India Open Super 750, Satwiksairaj Rankireddy and Chirag Shetty were the only Indians to make it to the semifinals. These results highlight the lack of reliable backup players beyond the top-ranked names.
 
Declining consistency among top players
 
While India has produced world-class shuttlers over the past decade, maintaining consistency has become an issue. Lakshya Sen, Kidambi Srikanth, and HS Prannoy were once among the most promising singles players, but their recent performances have been inconsistent. For Srikanth and Prannoy, age-related decline is understandable, but Sen's fluctuating form remains a concern. Emerging talents like Kiran George and Priyanshu Rajawat have shown promise, but they remain far from the level required to sustain India’s dominance on the world stage.

Women’s singles lacks successors
 
PV Sindhu has been India’s top women’s singles player for nearly a decade, but the gap between her and the next generation remains vast. Unlike Thailand, where multiple players have risen to elite levels, India’s upcoming women’s shuttlers like Malvika Bansod, Aakarshi Kashyap, and Ashmita Chaliha are yet to make a mark on the BWF World Tour. The introduction of Irwansyah Adi Pratama as a women's singles coach is a step toward bridging this gap, but it remains to be seen if it will yield results.
 
Doubles remains a major weakness
 
Beyond the successful pairing of Satwik-Chirag, India also continues to struggle in the doubles categories. At BAMTC, India lacked reliable men’s doubles options, with MR Arjun (WHO IS HIS PARTNER???) struggling to match the level of the world’s best pairs. Women’s doubles, however, shows some promise, with Treesa Jolly and Gayatri Gopichand slowly gaining momentum after missing out on the Olympics. Mixed doubles remains a weak link, with no significant breakthroughs despite several Indian pairs being ranked in the top 40. A stronger focus on doubles development is needed.
 
Urgent need for investment, planning
 
The failure to win a medal at Paris 2024 is a wake-up call for Indian badminton authorities. With the 2028 Olympics on the horizon, it is imperative to develop a stronger bench across all categories. The 2025 season offers a crucial window to rebuild, providing young players with opportunities to step up. Without systemic investment and long-term planning, Indian badminton risks losing its status as a powerhouse in the sport, especially as other nations strengthen their squads.
""",
    
 """Indian badminton star PV Sindhu has officially withdrawn from the 2025 Badminton Asia Mixed Team Championships (BAMTC), postponing her return to competitive action after her recent marriage.
The two-time Olympic medalist confirmed the decision on social media, revealing on Sunday that a hamstring injury sustained during training in Guwahati on February 4 has forced her to extend her recovery period.
"It is with a heavy heart that I share I won’t be travelling with the team for BAMTC 2025. While training on the 4th in Guwahati, I felt a twinge in my hamstring. Despite my efforts to push through with heavy taping for our country, an MRI has revealed that my recovery will take slightly longer than I initially expected. Wishing the team all the very best. I will be cheering from the sidelines," Sindhu wrote on X.
er absence is a significant blow to Team India, which is cur ..""",
    
    """Damascus (Syria), Feb 21 (AP) An official with the committee preparing a national dialogue conference in Syria to help chart the country's future said on Friday that it has not been decided whether the conference will take place before or after a new government is formed.
     The date of the conference has not been set and the timing “is up for discussion by the citizens”, Hassan al-Daghim, spokesperson for the committee, told The Associated Press in an interview in Damascus Friday.
     “If the transitional government is formed before the national dialogue conference, this is normal," he said. On the other hand, he said, “the caretaker government may be extended until the end of the national dialogue”.
     The conference will focus on drafting a constitution, the economy, transitional justice, institutional reform and how the authorities deal with Syrians, al-Daghim said. The outcome of the national dialogue will be non-binding recommendations to the country's new leaders.
     “However, these recommendations are not only in the sense of advise and formalities,” al-Daghim said. “They are recommendations that the President of the republic is waiting for in order to build on them.”
     After former President Bashir Assad was toppled in a lightning rebel offensive in December, Hayat Tahrir al-Sham, or HTS, the main former rebel group now in control of Syria, set up an interim administration comprising mainly of members of its “salvation government” that had ruled in northwestern Syria.
     They said at the time that a new government would be formed through an inclusive process by March. In January, former HTS leader Ahmad al-Sharaa was named Syria's interim president after a meeting of most of the country's former rebel factions.
     The groups agreed to dissolve the country's constitution, the former national army, security service and official political parties.
     The armed groups present at the meetings also agreed to dissolve themselves and for their members to be absorbed into the new national army and security forces. Notably absent was the Kurdish-led Syrian Democratic Forces, which holds sway in northeastern Syria.
     There has been international pressure for al-Sharaa to follow through on promises of an inclusive political transition. UN special envoy for Syria Geir Pedersen said this week that formation of a “new inclusive government” by March 1 could help determine whether Western sanctions are lifted as the country rebuilds.
     Al-Daghim said the decisions taken in the meeting of former rebel factions in January dealt with “security issues that concern the life of every citizen” and “these sensitive issues could not be postponed" to wait for an inclusive process.
     In recent weeks, the preparatory committee has been holding meetings in different parts of Syria to get input ahead of the main conference. Al-Daghim said that in those meetings, the committee had heard a broad consensus on the need for “transitional justice and unity of the country.”
     “There was a great rejection of the issue of quotas, cantons, federalization or anything like this," he said.
     But he said there was "disagreement on the order of priorities.” In the coastal cities of Latakia and Tartous, for instance, many were concerned about the low salaries paid to government workers, while in Idlib and suburbs of Damascus that saw vast destruction during nearly 14 years of civil war, reconstruction was the priority.
     The number of participants to be invited to the national conference has not yet been determined and may range from 400 to 1,000, al-Daghim said, and could include religious leaders, academics, artists, politicians and members of civil society, including some of the millions of Syrians displaced outside the country.
     The committee has said that the dialogue would include members of all of Syria's communities but that people affiliated with Assad's government and armed groups that refuse to dissolve and join the national army -- chief among them the SDF -- would not be invited.
     Al-Daghim said Syria's Kurds would be part of the conference even if the SDF is not.
     “The Kurds are a component of the people and founders of the Syrian state," he said. “They are Syrians wherever they are.” """,
    
    """
In a major step taken by the Uttar Pradesh Police Special Investigation Team (SIT) during the investigation of Sambhal violence, the police arrested close associate of auto thief and alleged mastermind of the November 24 Sambhal violence Shariq Sata on Thursday. Fugitive gangster Shariq Sata is on police radar for his suspected role in the violence. Last year, violence erupted in Sambhal over the court-ordered survey of a Mughal-era mosque, killing four people, officials said on Friday. 

The gangster, who is believed to be based in Dubai, is under probe for his alleged involvement in orchestrating criminal activities in India. Further, India TV has also learnt that the culprits conspire to assassinate Advocate Vishnu Shankar Jain during violence. Sambhal SP Krishan Kumar Vishnoi said that the aid of Shariq Sata confessed that there was a conspiracy to kill advocate Vishnu Shankar Jain during the Sambhal violence on 24th November 2024.

Police register 12 cases in connection with violence
As per the police, as many as 12 cases were registered in relation to Sambhal violence. Of the total 189 accused, 79 are yet to be arrested. Sambhal Superintendent of Police (SP) Krishna Kumar Vishnoi said, "A total of 12 cases were registered in connection with the violence, and chargesheets have been filed in six of them." "Of the 159 accused, 80 have been arrested, while 79 are still at large. Action will be taken only based on solid evidence and no innocent person will be targeted," he stressed but did not elaborate on the charges framed against the accused.

Action against Shariq Sata
On legal proceedings against Sata, Vishnoi said, "Conducting operations from outside India to influence activities within the country falls under the purview of BNS Section 48 (Abetment outside India for offence in country). Following the arrest of Ghulam (the arrested aide of the gangster), we will proceed with action against Sata under this section." He said that during an investigation into the case, police recovered a large cache of weapons, including 9mm cartridges from the Pakistan Ordnance Factory.

About the case registered against Sambhal MP Ziaur Rehman Barq, Vishnoi said police have sought data from WhatsApp and Meta. "Further action be taken only after gathering concrete evidence," he said. Dismissing allegations against Sata's wife, the police officer clarified, "There is no evidence to suggest that she was involved in any crime. However, Ghulam was in occasional contact with Sata through her mobile, which does not constitute a criminal offence."

When asked about a possible Dawood Ibrahim connection, Vishnoi said, "Any link will become clear if Sata is extradited and interrogated." On Ghulam's links with politicians, he said, "Merely naming someone is not evidence. In 2014, there was a case of firing on Sohail Iqbal, allegedly on the orders of the then MP. A case was registered on March 31, 2014, but no further political connections have emerged."

He also confirmed that they have the evidence of a plan to assassinate a Delhi-based lawyer. "We have proof, including WhatsApp exchanges between Ghulam and Mulla Afroz, where they shared images of a pistol before the incident. The pistol has been recovered," Vishnoi told reporters.
""",
"""
Fugitive gangster Shariq Sata is on police radar for his suspected role in the violence that erupted here in November last year over the court-ordered survey of a Mughal-era mosque, killing four people, officials said on Friday. An aide of Sata was arrested on Thursday, they said.

The gangster, who is believed to be based in Dubai, is under investigation for his alleged involvement in orchestrating criminal activities in India.

Sambhal Superintendent of Police (SP) Krishna Kumar Vishnoi said, "A total of 12 cases were registered in connection with the violence, and chargesheets have been filed in six of them."

"Of the 159 accused, 80 have been arrested, while 79 are still at large. Action will be taken only based on solid evidence and no innocent person will be targeted," he stressed but did not elaborate on the charges framed against the accused.

Asked about legal proceedings against Sata, Vishnoi said, "Conducting operations from outside India to influence activities within the country falls under the purview of BNS Section 48 (Abetment outside India for offence in country). Following the arrest of Ghulam (the arrested aide of the gangster), we will proceed with action against Sata under this section." He said that during an investigation into the case, police recovered a large cache of weapons, including 9mm cartridges from the Pakistan Ordnance Factory.

About the case registered against Sambhal MP Ziaur Rehman Barq, Vishnoi said police have sought data from WhatsApp and Meta. "Further action be taken only after gathering concrete evidence," he said.

Dismissing allegations against Sata's wife, the police officer clarified, "There is no evidence to suggest that she was involved in any crime. However, Ghulam was in occasional contact with Sata through her mobile, which does not constitute a criminal offence."

When asked about a possible Dawood Ibrahim connection, Vishnoi said, "Any link will become clear if Sata is extradited and interrogated." On Ghulam's links with politicians, he said, "Merely naming someone is not evidence. In 2014, there was a case of firing on Sohail Iqbal, allegedly on the orders of the then MP. A case was registered on March 31, 2014, but no further political connections have emerged."

He also confirmed that they have the evidence of a plan to assassinate a Delhi-based lawyer. "We have proof, including WhatsApp exchanges between Ghulam and Mulla Afroz, where they shared images of a pistol before the incident. The pistol has been recovered," Vishnoi told reporters.

On whether Sata was the sole mastermind of the violence, the SP said, "He cannot be declared the only key player at this stage. As more criminals are arrested and chargesheets are filed, a clearer picture will emerge." On November 19 last year, the local court passed an ex-parte order for a survey of the mosque by an advocate commissioner after taking note of a plea of the Hindu side claiming the mosque was built by Mughal emperor Babur in 1526 after demolishing a temple.

On November 24, during a second round of the survey, protesting locals clashed with security personnel which led to the death of four people and injuries to dozens.
""",
"""
Fugitive gangster Shariq Sata, suspected of inciting violence over a mosque survey in India, remains under police scrutiny. Operating from Dubai, Sata's possible involvement in orchestrating criminal activities is investigated. With 80 arrests made, authorities prepare to proceed under legal provisions as investigations reveal new evidence.

Fugitive gangster Shariq Sata is under intense police scrutiny for his alleged involvement in violence related to a court-ordered survey of a Mughal-era mosque last November. The violence resulted in four deaths, and authorities arrested an aide of Sata, indicating a sprawling investigation.

Believed to be operating from Dubai, Sata is suspected of orchestrating criminal acts in India. According to Sambhal Superintendent of Police Krishna Kumar Vishnoi, 12 cases emerged from the violence, with six chargesheets filed. Out of 159 accused individuals, 80 have been apprehended while 79 remain at large, emphasizing data-driven enforcement.

Officials reveal plans to proceed under Section 48 for Sata's alleged offshore criminal operations. Authorities recovered a substantial cache of weapons, reinforcing evidence against the accused. Investigations extend to connections with politicians, while dismissing involvement claims regarding Sata's wife. The probe continues with revelations on planned criminal activities, maintaining a vigilant pursuit of justice.
""",
"""
Sambhal: The Uttar Pradesh Police's Special Investigation Team (SIT) on Thursday submitted chargesheets in six cases related to the Sambhal violence that took place in November last year. The 4,000-page chargesheet revealed that Shariq Satha, who is believed to be living in the UAE, had orchestrated the violence, reported The Times of India. Five people were killed while 29 police personnel sustained injuries in the violence.

Satha is a native of Sambhal. He used to run a car theft gang that was reportedly involved in stealing 300 vehicles from Delhi-NCR. Satha has connections with Dawood Ibrahim and Pakistan's ISI and fled the country using a fake passport, reported TOI quoting the police.

There are 79 accused named in the chargesheet. All the accused are currently lodged in jail.

Court Releases Woman Accused In Sambhal Violence Case Due To Lack Of Evidence

"Satha's involvement came to light during the investigation, and based on evidence recovered by us, we can say that he orchestrated the violence. As of now, the chargesheets are submitted in the court against 79 people, including members of Satha's gang. This is the first lot of chargesheets, and we will file a supplementary chargesheet as the investigation progresses," Sambhal SP Krishan Kumar Bishnoi told the media house.

During the investigation, the police recovered foreign-made catridges from the violence and also "unusual money transfers to account holders" in the district. In thye chargesheet, Samajwadi Party MP Ziaur Rahman Barq and local MLA Iqbal Mahmood's son Suhail Iqbal were also reportedly named.

The violence erupted on November 24 last year in Sambhal during a court-ordered Archaeological Survey of India (ASI) survey of the Shahi Jama Masjid, a 500-year-old mosque in the district. The survey was initiated following claims that the mosque was constructed on the ruins of a Hindu temple allegedly demolished during the Mughal period.

A total of 12 FIRs were registered in connection with the violence. The SIT is investigating all the FIRs. Notably, bullets "manufactured in Pakistan and the US" were recovered from the spot.
""",

"""
The family of Israeli hostage Shiri Bibas says a body handed over by Hamas on Friday is hers.

"Our Shiri was murdered in captivity and has now returned home," the family said in a statement. Israel's forensic officials who have been examining the body are yet to confirm the identification.

Remains handed over by Hamas on Thursday which it said were those of Shiri Bibas turned out to be an unidentified woman, Israel said.

It comes as six living hostages are handed over by Hamas on Saturday as part of a ceasefire deal. More than 600 Palestinian prisoners will be freed by Israel in exchange.

Follow updates on the hostages release
Family mourns 'man of peace' as body returned
Return of bodies marks day of anguish for Israel
The Bibas family said: "For 16 months, we sought certainty, and now that we have it, there is no comfort in it, but we hope for the beginning of a closure."

Hamas previously said the mother and her two children were killed in an Israeli air strike.

Earlier, a senior Hamas official confirmed to the BBC that the handover of the new body from Hamas to the Red Cross had taken place on Friday evening.

Israel had accused Hamas of breaking the terms of the ceasefire deal after forensic testing showed the remains handed over on Thursday were not that of Shiri Bibas.

The bodies of her sons, Ariel and Kfir, were returned to Israel, as was that of another hostage, Oded Lifschitz.

Hamas spokesman Ismail al-Thawabta said in a post on X on Friday that Shiri's remains seemed to have been mixed up with other bodies under rubble after the air strike.

Israel has disputed the claim that Ariel and Kfir Bibas were killed in an airstrike, with Israel Defense Forces (IDF) spokesman Daniel Hagari telling a press conference "forensic findings", which have not been seen by the BBC, suggested the boys had been killed "deliberately".

He said evidence had been shared with "partners around the world so they can verify it".

Shiri, Ariel and Kfir Bibas were aged 32, four and nine months respectively when they were kidnapped during the Hamas attacks on Israel on 7 October 2023.

They were taken hostage along with the children's father, Yarden Bibas, 34, who was released alive by Hamas on 1 February.

Under the first phase of a ceasefire deal, which began on 19 January and lasts for 42 days, Hamas agreed to hand over 33 hostages in return for Israel freeing 1,900 Palestinian prisoners.

On Saturday, the armed group released Eliya Cohen, 27, Omer Shem Tov, 22, Tal Shohan, 40, and 23-year-old Omer Wenkert - all of whom were taken during the 7 October attacks.

Ethiopian-Israeli Avera Mengitsu, who was captured by Hamas in 2014, was also released. Hisham al-Sayed, a Bedouin Arab-Israeli held in Gaza since 2015, will be handed over separately. Israel is due to free 602 Palestinian prisoners.

In subsequent stages of the agreement, Hamas will release the remaining living hostages from Gaza and return the bodies of dead hostages. Israel has pledged to release more Palestinian prisoners.

In the 7 October attacks, about 1,200 people - mostly civilians - were killed and 251 others taken back to Gaza as hostages.

In response, Israel launched a massive military campaign against Hamas which has killed at least 48,319 Palestinians - mainly civilians - according to the Hamas-run Gaza health ministry.

""",
"""
The body handed over to Israel by Palestinian terror outfit Hamas on Friday has been confirmed to be that of hostage Shiri Bibas, her family said in a statement on Saturday. The development comes amid widespread outrage in Israel after the body returned earlier this week by Hamas, which it claimed to be that of Shiri Bibas, turned out to be someone else.

The 32-year-old mother of two had come to symbolise the ordeal of hostages taken by Hamas during its October 7, 2023, offensive.

"After the identification process, we received the news this morning that we had feared: our Shiri was murdered in captivity... She has returned home to her sons, her husband, her sister, and all her family to rest," a statement by the Bibas family said.

Shiri's husband, Yarden Bibas, was released by Hamas earlier this month after being in captivity for 484 days. On Thursday, Hamas handed over four bodies as part of a ceasefire deal that has paused the brutal war in Gaza.

The Palestinian outfit claimed the bodies were of Shiri, her two young sons, Kfir and Ariel, and another captive, Oded Lifshitz. However, forensic tests by Israeli authorities found the body to be not of Shiri Bibas, prompting outrage in the Jewish nation and concerns about the deal being upended.
An irate Israeli Prime Minister Benjamin Netanyahu said he would make "Hamas pay" for not returning the body of Shiri. In a hard-hitting video statement, Netanyahu said, "We will act with determination to bring Shiri home along with all our hostages - both living and dead - and ensure Hamas pays the full price for this cruel and evil violation of the agreement."

On Friday, Hamas released another body, which was confirmed to be of Shiri. The outfit said it had been "mistakenly mixed" with others who were buried under the rubble in Gaza.

Hamas has maintained that Shiri and her two children were killed in an Israeli airstrike in Gaza - a claim dismissed by Israel.

On Saturday, six more hostages will be returned by Hamas in exchange for more than 600 Palestinian prisoners. The ceasefire deal, which came into effect on January 19, has halted months of brutal fighting that killed 48,000 Palestinians in Gaza, triggering a humanitarian crisis."""
]

embeddings = model.encode(articles)
semantic_similarity_matrix = cosine_similarity(embeddings)

def extract_named_entities(text):
    doc = nlp(text)
    return set(ent.text.lower() for ent in doc.ents)

ner_sets = [extract_named_entities(article) for article in articles]

def jaccard_similarity(set1, set2):
    union = set1.union(set2)
    if not union:
        return 0.0
    return len(set1.intersection(set2)) / len(union)

num_articles = len(articles)
ner_similarity_matrix = np.zeros((num_articles, num_articles))
for i in range(num_articles):
    for j in range(num_articles):
        ner_similarity_matrix[i, j] = jaccard_similarity(ner_sets[i], ner_sets[j])

alpha = 0.7 
combined_similarity_matrix = alpha * semantic_similarity_matrix + (1 - alpha) * ner_similarity_matrix

combined_distance_matrix = 1 - combined_similarity_matrix

clustering = AgglomerativeClustering(
    n_clusters=None, 
    metric="precomputed", 
    linkage="average",  
    distance_threshold=0.5
)

labels = clustering.fit_predict(combined_distance_matrix)

clustered_articles = {}
for i, label in enumerate(labels):
    clustered_articles.setdefault(label, []).append(articles[i])

print("\nClustered News Articles:")
for cluster_id, cluster in clustered_articles.items():
    print(f"\nCluster {cluster_id + 1}:")
    for article in cluster:
        print(f"- {article[:100]}...") 

ner_results = {article: list(extract_named_entities(article)) for article in articles}