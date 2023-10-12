# Beyond the Bedside: Evaluating Hospital Quality of Care amidst Workforce Shortages

## Presented virtually at Fullstack Academy's DATA Capstone Showcase on September 28, 2023.  <em>[View the presentation slides here.](https://drive.google.com/file/d/1JkWIu11GYg6cP4orZzCSExup0sfWPnJl/view)</em>

## How does the shortage of healthcare professionals in the U.S. impact the quality of care provided in acute care hospitals?

### The Rationale

My last job before DATA was as a certified nurse assistant (CNA) at a private hospital that was recently acquired by a larger hospital network.  Working at this hospital was a transformative experience, and really made me sensitive to how factors like staffing and cultural competence (especially in areas with diverse patient populations) can affect quality of care.

I worked on a Med/Surg unit where we had weekly huddles to discuss how our unit (and the hospital) was performing in terms of patients falls, infection control, patient satisfaction, etc.  On the job, I was hypersensitive to the importance of infection control, especially for surgical patients, to prevent issues like surgical site infections, CAUTIs, and spread of C. diff.  Having had practical experience with some of the sub-measures comprising the Quality of Care domain groups, I was interested in investigating these measures from a data perspective.

I'm also very interested in this topic area because during the time when I contemplated going to medical school, it was always my desire to apply to residency programs in regions of the country with the highest need for medical doctors.

### The Audience

One potential audience = Executives at hospitals operating in shortage areas, who are incentivized by the Centers for Medicare & Medicaid Services (CMS) Hospital Value-Based Purchasing (VBP) Program to identify areas for improvement at their hospitals.  (The CMS rewards hospitals with payments based on quality of care, as assessed by measures related to several domains: mortality, safety of care, readmission, patient experience, effectiveness of care, timeliness of care, & efficient use of medical imaging.)

Second potential audience = Early-career healthcare professionals (e.g. physicians, nurse practitioners, physician assistants) transitioning from training to practice, who are seeking to identify high-need regions and hospitals that could benefit from additional workforce.

### The Questions

1) Which states in the U.S. are facing the most severe shortages of healthcare professionals?  (I will look at HPSA Score.)

2) Which states have the lowest quality of care metrics within their hospitals?  (I will look at Overall Hospital Quality Star Rating.)

3) How do the quality of care metrics compare between hospitals in regions classified as shortage areas versus those that are not?  (I will look at the sub-domain measures that make up the star rating.)

### The Expectations

I expect that rural areas in the U.S. might have the most severe shortages of healthcare professionals, while urban areas might have less.  I also expect that areas with a greater percent of their population below the federal poverty level might have a greater need for practitioners.

I also expect that the hospitals with the lowest quality of care metrics might be located in regions classified as health professional shortage areas.  I have no strong expectations about which of the five measure groups (mortality, safety, readmission, patient experience, timely & effective care) might have the lowest scores.

### The Results

U.S. states in the South, specifically Mississippi, Alabama, & Louisiana, have a large proportion of acute care hospitals exhibiting a shortage of primary care physicians.  Counterintuitively, for Mississippi & Alabama, hospitals in shortage areas have a higher average Hospital Quality Star Rating than non-shortage area hospitals.

When comparing shortage area hospitals to non-shortage area hospitals in these three states, a majority of shortage area hospitals are actually performing at or above the national average in the quality of care sub-domain measures.

### Data Sources

[Health Resources & Services Administration (HRSA)](https://data.hrsa.gov/data/download) - Healthcare Professional Shortage Areas

[Centers for Medicare & Medicaid Services (CMS)](https://data.cms.gov/provider-data/topics/hospitals) - Hospital Compare (2016 - 2023)