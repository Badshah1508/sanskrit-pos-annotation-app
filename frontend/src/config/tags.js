// Approved Sanskrit Consortium POS Tag Inventory
// As specified: N, NS, NV, KNV, SN, SNV, SNS, SAM, SAMY, SAMP, KP, UP, AVN, AVP, AVUP, SAMB, AVU, K, AKV, AB, AVC, DVI, A

export const SANSKRIT_CONSORTIUM_TAGS = [
  { tag: 'N', name: 'Noun (नामपदम्)', description: 'General noun stem or inflected noun' },
  { tag: 'NS', name: 'Proper Noun (विशेषनाम)', description: 'Specific name of person, place, or entity' },
  { tag: 'NV', name: 'Verbal Noun / Kridanta (कृदन्तरूपम्)', description: 'Participle or noun derived from verbal root' },
  { tag: 'KNV', name: 'Secondary Derivative / Taddhita (तद्धितः)', description: 'Secondary noun derived from another noun' },
  { tag: 'SN', name: 'Pronoun (सर्वनाम)', description: 'Pronoun (tat, etat, aham, etc.)' },
  { tag: 'SNV', name: 'Pronominal Adjective (सर्वनाम-विशेषणम्)', description: 'Pronoun acting as modifier' },
  { tag: 'SNS', name: 'Compound Pronoun (समस्तसर्वनाम)', description: 'Pronominal element in compound' },
  { tag: 'SAM', name: 'Compound Initial Member (पूर्वपदम्)', description: 'First member of a samasa (compound word)' },
  { tag: 'SAMY', name: 'Compound Middle Member (मध्यपदम्)', description: 'Intermediate member in a complex compound' },
  { tag: 'SAMP', name: 'Compound Final Member (उत्तरपदम्)', description: 'Last member carrying case ending in compound' },
  { tag: 'KP', name: 'Finite Verb (तिङन्तरूपम् / क्रियापदम्)', description: 'Inflected verb with lakara and purusha/vachana' },
  { tag: 'UP', name: 'Prefix / Upasarga (उपसर्गः)', description: 'Pre-verb prefix (pra, para, sam, ni, etc.)' },
  { tag: 'AVN', name: 'Indeclinable / Avyaya (सामान्य-अव्ययम्)', description: 'Pure indeclinable particle (ca, eva, api, tu)' },
  { tag: 'AVP', name: 'Adverbial Indeclinable (क्रियाविशेषणम्)', description: 'Indeclinable acting as an adverb' },
  { tag: 'AVUP', name: 'Indeclinable with Prefix', description: 'Compound indeclinable starting with upasarga' },
  { tag: 'SAMB', name: 'Conjunction (संयोजकम् / सम्बन्धकः)', description: 'Coordinating or subordinating connective' },
  { tag: 'AVU', name: 'Interjection (विस्मयादिबोधकम्)', description: 'Exclamatory or emotional particle' },
  { tag: 'K', name: 'Karmapravachaniya (कर्मप्रवचनीयः)', description: 'Governing particle governing a specific vibhakti' },
  { tag: 'AKV', name: 'Auxiliary / Secondary Verb', description: 'Auxiliary verb element' },
  { tag: 'AB', name: 'Abbreviation (संक्षेपः)', description: 'Abbreviated word or symbol' },
  { tag: 'AVC', name: 'Numerical / Quantifier Indeclinable', description: 'Indeclinable number or quantitative marker' },
  { tag: 'DVI', name: 'Reduplicated Form (द्विरुक्तम्)', description: 'Repeated word for emphasis or frequency' },
  { tag: 'A', name: 'Adjective / Visheshana (विशेषणम्)', description: 'Qualifying adjective modifying a noun' }
];

export const VALID_TAG_SET = new Set(SANSKRIT_CONSORTIUM_TAGS.map(t => t.tag));
