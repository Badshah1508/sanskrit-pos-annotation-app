# Sanskrit POS Annotation & Expert Verification Portal
## Comprehensive User Manual for Sanskrit Language Experts & Scholars

---

### 1. Introduction & Research Purpose

Welcome to the **Sanskrit Part-of-Speech (POS) Annotation & Expert Verification Portal**. 

This web application has been developed as part of an M.Tech Data Science dissertation on **Cross-Domain Sanskrit POS Tagging**, focusing on the contemporary **Sanskrit News Domain**.

#### Why is Your Expert Role Critical?
Automatic computational tools (such as the Stanza Sanskrit NLP model) often encounter challenges with Sanskrit news sentences due to complex compounds (*samāsa*), morpho-syntactic nuances, and rich inflection (*vibhakti*). 
To establish a high-accuracy, peer-reviewed **Gold Standard Dataset**, your linguistic verification is essential. Your judgment ensures that computational linguistics models can be properly trained and evaluated against authoritative scholarly annotations.

---

### 2. How to Access the Portal

The application is hosted online with a secure HTTPS connection and works seamlessly on **any modern browser (Google Chrome, Firefox, Safari, Edge)**:

* 🌐 **Web Portal Link:** [https://sanskrit-pos-annotation-app.vercel.app/](https://sanskrit-pos-annotation-app.vercel.app/)
* 📱 **Device Compatibility:** Works on **Laptops, Desktops, iPads/Tablets, and Mobile Phones**.

---

### 3. Step-by-Step Login Instructions

You do **not** need to create an account or install any software. A verified scholar account has already been prepared for you.

1. Open the link: **[https://sanskrit-pos-annotation-app.vercel.app/](https://sanskrit-pos-annotation-app.vercel.app/)**
2. On the **Expert Login** page, enter the default credentials:
   * **Username:** `sanskrit_scholar`
   * **Password:** `password123`
3. Click the **"Sign In"** button.
4. You will immediately be taken to the Scholar Dashboard.

*(Note: Your session will stay active in your browser. When you return later, you will automatically resume where you left off).*

---

### 4. Scholar Dashboard Overview

Upon logging in, the Dashboard presents:
* **Corpus Statistics:** Real-time metrics showing total sentences, sentences awaiting review (Pending), partial drafts (In Progress), and finalized sentences (Verified).
* **Overall Progress Bar:** Visual indicator tracking overall corpus completion.
* **Resume Annotation Button:** Click **"▶ Resume Annotation"** to jump directly to your next sentence in the queue.

---

### 5. The Annotation Screen Walkthrough

The annotation screen is designed for comfortable reading of Devanagari Sanskrit text:

#### A. Sentence Header Information
* **Document ID & Sentence ID:** Provenance identifying the original news article.
* **Annotation ID (e.g., `1_6`):** The unique database identifier for this sentence.
* **Unassigned Tracker:** A live counter in the top-right (e.g., `⚠️ 3 of 9 tokens unassigned` or `✓ All 9 tokens assigned`).

#### B. Original Sanskrit Sentence (मूलवाक्यम्)
The complete Sanskrit sentence is prominently displayed in high-resolution Devanagari typography at the top of the workspace.

#### C. Token Annotation Area
Every token in the sentence is listed in its exact original order.
* **On Laptop/Desktop:** Displayed as an organized table.
* **On Tablet/Mobile Phone:** Displayed as spacious touch-friendly cards for easy tapping.

Each token displays:
1. **Token Number (#):** 1, 2, 3... preserving word order.
2. **Token (पदम्):** The Sanskrit word in Devanagari script.
3. **Lemma (मूलरूपम्):** The dictionary headword / verbal root (if detected).
4. **Stanza UPOS (अनुमानितम्):** An **automated reference badge** (e.g., `NOUN`, `VERB`).  
   *(⚠️ Important: This is only a computer-generated baseline hint. Please do not assume it is correct; your expert judgment is authoritative).*
5. **Morphological Features:** Case (*vibhakti*), number (*vacana*), or gender hints.
6. **Expert Sanskrit POS Tag (The Core Task):** The interactive dropdown selector.

---

### 6. Approved Sanskrit Consortium POS Tag Inventory

Please assign one tag from the 23 approved **Sanskrit Consortium POS tags** to every token:

| Tag Code | Sanskrit Name | English Description | Example |
|:---:|:---|:---|:---|
| **N** | नामपदम् (General Noun) | Common noun stem or inflected noun | विद्या, छात्रेण, मतिः |
| **NS** | विशेषनाम (Proper Noun) | Specific person, city, river, organization | नरेन्द्रमोदी, भारतस्य, नवदेहल्याम् |
| **NV** | कृदन्तरूपम् (Verbal Noun) | Participle / noun derived from a verbal root | गमनम्, उद्घाटितवान्, पठितः |
| **KNV** | तद्धितान्तरूपम् (Secondary Derivative) | Noun derived from another noun | भारतीयः, धार्मिकम् |
| **SN** | सर्वनाम (Pronoun) | Personal, relative, or interrogative pronoun | अहम्, तत्, एषः, अस्याः, किम् |
| **SNV** | सर्वनाम-विशेषणम् (Pronominal Adjective) | Pronoun acting as a demonstrative modifier | *तस्मिन्* वने, *सर्वे* जनाः |
| **SNS** | समस्तसर्वनाम (Compound Pronoun) | Pronominal member inside a compound | मत्प्रिय, तत्सदृश |
| **SAM** | पूर्वपदम् (Compound Initial Member) | First member of a samāsa (compound) | *राम*लक्ष्मणौ (*राम* is SAM) |
| **SAMY** | मध्यपदम् (Compound Middle Member) | Intermediate member in a multi-word compound | धर्म*कर्म*विपाकः |
| **SAMP** | उत्तरपदम् (Compound Final Member) | Last member bearing the inflected ending | राम*लक्ष्मणौ* (*लक्ष्मणौ* is SAMP) |
| **KP** | क्रियापदम् / तिङन्तम् (Finite Verb) | Inflected verb with lakāra and puruṣa/vacana | वर्तते, भवति, गमिष्यति, अकरोत् |
| **UP** | उपसर्गः (Prefix / Upasarga) | Pre-verb verbal prefix standing separately | प्र, सम्, अनु, वि |
| **AVN** | सामान्य-अव्ययम् (Indeclinable Particle) | Non-inflecting particle, including punctuation | च, अपि, एव, तथा, ।, ? |
| **AVP** | क्रियाविशेषणम् (Adverbial Indeclinable) | Indeclinable modifying a verb | सर्वदा, सर्वथा, अद्य, शनैः |
| **AVUP** | सोपसर्ग-अव्ययम् (Indeclinable with Prefix) | Compound indeclinable starting with upasarga | प्रत्यहम्, यथाशक्ति |
| **SAMB** | सम्बन्धकः / संयोजकम् (Conjunction) | Coordinating or subordinating connective | यतः, तथापि, यद्यपि, चेत् |
| **AVU** | विस्मयादिबोधकम् (Interjection) | Exclamatory or emotional particle | अहो, हा, हन्त, भोः |
| **K** | कर्मप्रवचनीयः (Karmapravacanīya) | Governing preposition governing a vibhakti | प्रति, अनु, अन्तरेण |
| **AKV** | सहायक्रिया (Secondary / Auxiliary Verb) | Auxiliary verb element | अस्ति (when auxiliary) |
| **AB** | संक्षेपः (Abbreviation) | Abbreviated word or symbol | डॉ., सं. |
| **AVC** | संख्यावाच्यव्ययम् (Quantifier Indeclinable) | Numerical or quantitative particle | सकृत्, त्रिः, बहुशः |
| **DVI** | द्विरुक्तम् (Reduplicated Word) | Repeated word for frequency or emphasis | शनैः शनैः, पुनः पुनः |
| **A** | विशेषणम् (Qualifying Adjective) | Descriptive adjective qualifying a noun | नूतनम्, प्राचीनतमा, समृद्धा |

---

### 7. Actions & Verification Workflow

At the bottom of the annotation screen, you will find two primary action buttons:

#### 1. 💾 Save Draft
* **When to use:** Use this if you have partially annotated a sentence and need to take a break, leave your computer, or research an ambiguous compound.
* **What happens:** 
  * The tags you have selected so far are securely saved in the database.
  * Any optional notes you typed are saved.
  * The sentence status becomes `In Progress`.
  * The sentence is **not** counted as verified yet.
  * When you log back in later, your saved tags will be right there waiting for you.

#### 2. ✓ Save & Next
* **When to use:** Use this when you have reviewed the sentence and assigned an approved tag to **every single token**.
* **What happens:**
  * The application validates that no token has been left unassigned.
  * All tags and notes are saved in a single permanent transaction.
  * The sentence is officially marked as `Verified`.
  * Your scholar username and current timestamp are permanently recorded.
  * A green success banner appears, and the **next pending sentence loads automatically**!

---

### 8. What Happens If You Miss a Word and Click "Save & Next"?

The system has a built-in **Data Integrity Guard** to prevent accidental incomplete submissions:

1. **The System Will Block the Submission:**
   * It will **never** save an incomplete sentence as verified.
2. **Clear Warning Message:**
   * A prominent notification appears at the top:
     > `Cannot verify sentence: Missing approved POS tags for tokens: #3 'छात्राणां', #6 'सर्वथा'. Please assign all tags before clicking Save & Next.`
3. **Visual Highlighting:**
   * Any unassigned token remains highlighted with an **amber/gold border** (`-- Select Tag --`) so you can spot it instantly.
4. **Nothing is Lost:**
   * All the tags you already assigned remain intact on your screen. You do **not** have to re-enter anything.
   * Simply select the tag for the highlighted missing words and click **Save & Next** again.

---

### 9. Leaving With Unsaved Changes

If you make modifications to a tag and accidentally try to navigate away (such as clicking *"Back to Dashboard"*), the application will protect your work by showing a confirmation prompt:

> **"Discard Unsaved Changes?"**  
> *You have unsaved tag modifications in this sentence. If you leave now without saving, your changes will be lost.*  
> `[Keep Editing]` / `[Discard Changes]`

Click **Keep Editing** to stay on the page and click **Save Draft** or **Save & Next**.

---

### 10. Optional Scholar Remarks / Notes

At the bottom of the token list, there is an optional text box labeled:
> **Annotation Note / Scholar Remarks (optional):**

Feel free to write linguistic observations here, such as:
* Notes on compound resolution (*samāsa-vigraha*).
* Sandhi segmentation ambiguities.
* Rare grammatical forms or Vedic archaisms.
These notes will be preserved alongside your verified tags in the final dissertation dataset.

---

### 11. Quick Summary Checklist for Scholars

1. Open **[https://sanskrit-pos-annotation-app.vercel.app/](https://sanskrit-pos-annotation-app.vercel.app/)**
2. Login with `sanskrit_scholar` / `password123`.
3. Click **"▶ Resume Annotation"**.
4. Read the Devanagari sentence.
5. Select a tag for each word from the dropdown.
6. Click **"Save Draft"** if pausing, or **"Save & Next"** to finalize and advance.
7. Repeat at your own pace!

Thank you for your invaluable scholarly contribution to Sanskrit Computational Linguistics!
