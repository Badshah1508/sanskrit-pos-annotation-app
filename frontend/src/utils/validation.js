import { VALID_TAG_SET } from '../config/tags';

/**
 * Validates whether all tokens in a sentence have been assigned a valid Sanskrit Consortium POS tag.
 *
 * @param {Array} tokens - List of token objects
 * @returns {Object} { isValid: boolean, missingTokens: Array, errors: Array }
 */
export function validateSentenceForVerification(tokens) {
  const errors = [];
  const missingTokens = [];

  if (!tokens || tokens.length === 0) {
    return {
      isValid: false,
      missingTokens: [],
      errors: ['No tokens found in sentence.']
    };
  }

  tokens.forEach((token) => {
    const tag = token.gold_sanskrit_tag;
    if (!tag || tag.trim() === '') {
      missingTokens.push({
        token_id: token.token_id,
        token: token.token
      });
    } else if (!VALID_TAG_SET.has(tag.trim())) {
      errors.push(`Token "${token.token}" has invalid tag "${tag}".`);
    }
  });

  if (missingTokens.length > 0) {
    errors.push(
      `${missingTokens.length} token(s) are missing an assigned Sanskrit Consortium tag.`
    );
  }

  return {
    isValid: errors.length === 0,
    missingTokens,
    errors
  };
}
