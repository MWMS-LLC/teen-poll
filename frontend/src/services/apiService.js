import axios from 'axios';
import API_BASE from '../config.js';

/**
 * Fetch all categories -> Landing.jsx
 * @returns {Promise<Array>} List of categories
 */
export async function fetchCategories() {
  const res = await axios.get(`${API_BASE}/api/categories`);
  console.log("Fetched categories:", res.data.categories);
  return res.data.categories;
}


/**
 * Fetch all blocks for a category -> Category.jsx
 * @param {number} categoryId 
 * @returns {Promise<Array>} List of blocks
 */
export async function fetchBlocks(categoryId) {
  const res = await axios.get(`${API_BASE}/api/categories/${categoryId}/blocks`);
  return res.data.blocks;
}

/**
 * Fetch all questions for a block -> Block.jsx
 * @param {string} blockCode 
 * @returns {Promise<Array>} List of questions
 */
export async function fetchQuestions(blockCode) {
  const res = await axios.get(`${API_BASE}/api/blocks/${blockCode}/questions`);
  return res.data.questions;
}

/**
 * Fetch all options for a question -> Question.jsx in components
 * @param {string} questionCode 
 * @returns {Promise<Array>} List of options
 */
export async function fetchOptions(questionCode) {
  const res = await axios.get(`${API_BASE}/api/questions/${questionCode}/options`);
  return res.data; // backend returns array directly
}

/**
 * Create a new user
 * @param {string} userUuid 
 * @param {number} birthYear 
 * @returns {Promise<Object>} Created user
 */
export async function createUser(userUuid, birthYear) {
  const res = await axios.post(
    `${API_BASE}/api/users?user_uuid=${userUuid}&year_of_birth=${birthYear}`
  );
  return res.data;
}


/**
 * Submit a single-choice (radio) vote
 * @param {string} questionCode
 * @param {string} optionSelect
 * @param {string} userUuid
 * @param {string} otherText - optional text for "OTHER" option
 */
export async function submitVote(questionCode, optionSelect, userUuid, otherText = null) {
  const res = await axios.post(`${API_BASE}/api/vote/single`, {
    question_code: questionCode,
    option_select: optionSelect,
    user_uuid: userUuid,
    other_text: otherText
  });
  return res.data;
}

/**
 * Submit checkbox vote
 * @param {string} questionCode
 * @param {Array<string>} optionSelects
 * @param {string} userUuid
 * @param {string} otherText - optional text for "OTHER" option
 */
export async function submitCheckboxVote(questionCode, optionSelects, userUuid, otherText = null) {
  const res = await axios.post(`${API_BASE}/api/vote/checkbox`, {
    question_code: questionCode,
    option_selects: optionSelects,
    user_uuid: userUuid,
    other_text: otherText
  });
  return res.data;
}

/**
 * Submit "OTHER" text vote
 * @param {string} questionCode
 * @param {string} otherText
 * @param {string} userUuid
 */
export async function submitOtherVote(questionCode, otherText, userUuid) {
  const res = await axios.post(`${API_BASE}/api/vote/other`, {
    question_code: questionCode,
    other_text: otherText,
    user_uuid: userUuid
  });
  return res.data;
}

/**
 * Fetch results for a question
 * @param {string} questionCode
 */
export async function fetchResults(questionCode) {
  const res = await axios.get(`${API_BASE}/api/results/${questionCode}`);
  return res.data;
}
