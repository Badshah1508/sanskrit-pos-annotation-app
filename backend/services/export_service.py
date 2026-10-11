import io
import csv
from sqlalchemy.orm import Session
from models import Sentence, Token

EXPORT_COLUMNS = [
    "doc_id", "sentence_id", "annotation_id", "sentence_text",
    "token_id", "token", "lemma", "upos", "stanza_upos", "xpos", "feats",
    "gold_sanskrit_tag", "annotation_status", "annotation_note",
    "verified_by", "verified_at"
]

def generate_verified_csv(db: Session) -> io.StringIO:
    """
    Exports verified Sanskrit POS sentences as a UTF-8 formatted CSV string.
    Only includes verified sentences and preserves original token ordering.
    """
    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens Sanskrit/Devanagari text correctly without garbled characters
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(EXPORT_COLUMNS)

    verified_sentences = (
        db.query(Sentence)
        .filter(Sentence.status == "verified")
        .order_by(Sentence.id)
        .all()
    )

    for sent in verified_sentences:
        v_at = sent.verified_at.isoformat() if sent.verified_at else ""
        for token in sent.tokens:
            row = [
                sent.doc_id,
                sent.sentence_id,
                sent.annotation_id,
                sent.sentence_text,
                token.token_id,
                token.token,
                token.lemma or "",
                token.upos or "",
                token.stanza_upos or "",
                token.xpos or "",
                token.feats or "",
                token.gold_sanskrit_tag or "",
                sent.status,
                sent.annotation_note or "",
                sent.verified_by or "",
                v_at
            ]
            writer.writerow(row)

    output.seek(0)
    return output
