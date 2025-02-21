from transformers import pipeline

# Initialize the summarization pipeline (BART)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = summarizer.tokenizer

# Explicitly set the tokenizer's maximum input length (for safety).
# (Even if BART is pretrained with a fixed size, you can force a value.)
tokenizer.model_max_length = 1024  
MAX_CHUNK_TOKENS = 1200  # Maximum tokens per chunk for our recursive splitting.
MIN_CHUNK_TOKENS = 600   # Minimum tokens each of the final two chunks should have.
MIN_TOTAL_LAST = 2 * MIN_CHUNK_TOKENS  # At least 1200 tokens total for the last two chunks.

def recursive_summarize(text, min_tokens=MIN_CHUNK_TOKENS, max_tokens=MAX_CHUNK_TOKENS):
    """
    Recursively summarizes the input text until it can fit in one chunk.
    
    Steps:
      1. Tokenize the text.
      2. If the total token count is <= max_tokens, return the text (base case).
      3. Otherwise, split tokens into chunks:
         - The first N chunks are full chunks of size max_tokens.
         - The remaining tokens (the "last part") are split into two nearly equal chunks,
           ensuring each is at least min_tokens. If the remainder is too small (< MIN_TOTAL_LAST),
           one full chunk is pulled back to help.
      4. Summarize each chunk individually.
      5. Combine the summaries into one text and call recursive_summarize() on it.
    """
    # Tokenize the text (without adding special tokens)
    all_tokens = tokenizer.encode(text, add_special_tokens=False)
    total_tokens = len(all_tokens)
    print(f"Total tokens: {total_tokens}")
    
    # Base case: if the text is short enough, return it.
    if total_tokens <= max_tokens:
        return text
    
    # Determine how many full chunks of size max_tokens we have.
    full_chunks = total_tokens // max_tokens
    remainder = total_tokens % max_tokens
    
    # If remainder is less than needed to form two chunks (i.e. less than MIN_TOTAL_LAST)
    # and we have at least one full chunk, pull one full chunk back.
    if full_chunks >= 1 and remainder < MIN_TOTAL_LAST:
        full_chunks -= 1
        start_last = full_chunks * max_tokens
        last_tokens = all_tokens[start_last:]
    else:
        start_last = full_chunks * max_tokens
        last_tokens = all_tokens[start_last:]
    
    # Build the list of token chunks.
    chunks_tokens = []
    # Add full chunks.
    for i in range(full_chunks):
        chunk = all_tokens[i * max_tokens : (i + 1) * max_tokens]
        chunks_tokens.append(chunk)
    
    # For the final tokens, split them into two nearly equal parts.
    last_total = len(last_tokens)
    split_index = last_total // 2
    # Ensure each final chunk is at least min_tokens.
    if split_index < min_tokens or (last_total - split_index) < min_tokens:
        split_index = min_tokens
        if last_total - split_index < min_tokens:
            # If even after adjustment the last part is too short, just add it as one chunk.
            chunks_tokens.append(last_tokens)
        else:
            chunks_tokens.append(last_tokens[:split_index])
            chunks_tokens.append(last_tokens[split_index:])
    else:
        chunks_tokens.append(last_tokens[:split_index])
        chunks_tokens.append(last_tokens[split_index:])
    
    # Decode token chunks back into text.
    chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks_tokens]
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
        print(f"Chunk {i+1}: {chunk_len} tokens")
    
    # Summarize each chunk individually.
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
        print(f"\nSummarizing chunk {i+1}/{len(chunks)} (token length: {chunk_len})...")
        try:
            # You can adjust max_length/min_length for the chunk summaries.
            summary_chunk = summarizer(
                chunk,
                max_length=600,
                min_length=400,
                do_sample=False,
                truncation=True
            )
            chunk_summaries.append(summary_chunk[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk {i+1}: {e}")
            chunk_summaries.append(chunk)
    
    combined_summary = " ".join(chunk_summaries)
    print("\nCombined Intermediate Summary:")
    print(combined_summary)
    
    # Recursively summarize the combined summary until it fits within one chunk.
    return recursive_summarize(combined_summary, min_tokens, max_tokens)

# Example usage with provided texts:
texts = ["""
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
"""]

final_summary_text = recursive_summarize(" ".join(texts))
print("\nFinal Recursive Summary:")
print(final_summary_text)
