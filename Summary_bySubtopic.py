import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from transformers import AutoTokenizer



# Sample news articles with varied topics

# Sample news articles with 2 similar subtopics & 2 distinct ones
# articles = [
#     """LeBron James led the Lakers to a 115-108 victory over the Boston Celtics. 
#     Scoring 32 points with 10 assists, he showcased his dominance. 
#     The Celtics, despite a strong start, struggled with turnovers in the second half, 
#     allowing the Lakers to secure a crucial comeback win.""",  # Sports - NBA

#     """The Kansas City Chiefs secured a dramatic overtime win in the Super Bowl against the San Francisco 49ers. 
#     Patrick Mahomes orchestrated a game-winning drive in the final moments, sealing his legacy as one of the greatest quarterbacks. 
#     The thrilling finish left fans in awe.""",  # Sports - NFL (same subtopic: Sports)

#     """The U.S. Senate has approved a $1.2 trillion infrastructure bill aimed at modernizing roads, bridges, and broadband. 
#     The bipartisan legislation is expected to create jobs, but critics warn of excessive government spending. 
#     President Biden hailed it as a transformative step for America's future.""",  # Politics

#     """The highly anticipated sequel to 'Dune' premiered last night to widespread acclaim. 
#     Critics praised Denis Villeneuve's breathtaking visuals and Timothée Chalamet's performance. 
#     The film is already being considered a strong contender for multiple Oscar nominations.""",  # Entertainment
# ]
# articles = [
#     """India was one of the top nations in badminton only a few years ago, with players like PV Sindhu and Saina Nehwal securing golds year after year at multiple events, including the Olympics...""",
    
#     """Indian badminton star PV Sindhu has officially withdrawn from the 2025 Badminton Asia Mixed Team Championships (BAMTC)...""",
    
#     """The 2025 Badminton Asia Mixed Team Championships saw multiple top players withdraw due to injuries...""",
    
#     """The stock market experienced a major downturn, with tech companies losing significant value...""",
    
#     """Fugitive gangster Shariq Sata is on police radar for his suspected role in the violence that erupted...""",
    
#     """Sambhal: The Uttar Pradesh Police's Special Investigation Team (SIT) on Thursday submitted chargesheets..."""
# ]

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
"""
]




# Step 1: Convert Articles into Embeddings
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # More accurate model for long texts
embeddings = model.encode(articles, normalize_embeddings=True)

# Step 2: Clustering with Agglomerative Clustering
clustering_model = AgglomerativeClustering(n_clusters=None, distance_threshold=1.2, linkage='ward')
labels = clustering_model.fit_predict(embeddings)

# Step 3: Group Articles by Cluster
subtopic_clusters = {}
for i, label in enumerate(labels):
    subtopic_clusters.setdefault(label, []).append(articles[i])

# Step 4: Generate Subtopic Names
subtopic_names = {}
# for cluster, grouped_articles in subtopic_clusters.items():
   


# subtopic_clusters = {}
# for i, label in enumerate(labels):
#     subtopic_clusters.setdefault(label, []).append(articles[i])

# Print clusters before summarizing
print("\n### Clustered Articles ###\n")
for cluster, grouped_articles in subtopic_clusters.items():
    print(f"Cluster {cluster}:")
    subtopic_names[cluster] = grouped_articles[0][:50] + "..."  # Take first few words for naming
    for article in grouped_articles:
        print(f"- {article[:100]}...")  # Print the first 100 characters for readability
    print("\n" + "-"*80 + "\n")
# Step 5: Summarize Each Cluster
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# subtopic_summaries = {}
# for cluster, grouped_articles in subtopic_clusters.items():
#     combined_text = " ".join(grouped_articles)  # Merge articles under one subtopic
#     summary = summarizer(combined_text, max_length=200, min_length=100, do_sample=False)  # Longer summaries
#     tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
#     tokens = tokenizer(combined_text, truncation=True, max_length=1024, return_tensors="pt")
#     subtopic_summaries[subtopic_names[cluster]] = summary[0]['summary_text']

# # Print the results
# print("\n### Topic: Various News Categories ###\n")
# for subtopic, summary in subtopic_summaries.items():
#     print(f"**Subtopic:** {subtopic}")
#     print(f"**Summary:** {summary}\n")
