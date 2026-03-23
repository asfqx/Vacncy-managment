const WIDOW_WORDS = [
  "а",
  "без",
  "бы",
  "в",
  "во",
  "да",
  "для",
  "до",
  "же",
  "за",
  "и",
  "из",
  "к",
  "ко",
  "ли",
  "на",
  "над",
  "не",
  "ни",
  "но",
  "о",
  "об",
  "обо",
  "от",
  "по",
  "под",
  "при",
  "про",
  "с",
  "со",
  "у",
];

const WIDOW_PATTERN = new RegExp(
  `(^|[\\s([{"«„])(${WIDOW_WORDS.join("|")})\\s+(?=\\S)`,
  "giu"
);

const ATTRIBUTE_NAMES = ["placeholder", "title", "aria-label"];
const SKIP_TAGS = new Set(["CODE", "KBD", "PRE", "SCRIPT", "STYLE", "TEXTAREA"]);

function preventWidows(text) {
  if (!text || !/[А-Яа-яЁё]/u.test(text)) {
    return text;
  }

  return text.replace(WIDOW_PATTERN, (_, prefix, word) => `${prefix}${word}\u00A0`);
}

function shouldSkipElement(element) {
  if (!element) {
    return false;
  }

  if (SKIP_TAGS.has(element.tagName)) {
    return true;
  }

  return element.isContentEditable;
}

function processTextNode(node) {
  const parent = node.parentElement;
  if (!parent || shouldSkipElement(parent)) {
    return;
  }

  const formatted = preventWidows(node.nodeValue);
  if (formatted !== node.nodeValue) {
    node.nodeValue = formatted;
  }
}

function processAttributes(element) {
  if (shouldSkipElement(element)) {
    return;
  }

  for (const attribute of ATTRIBUTE_NAMES) {
    const value = element.getAttribute(attribute);
    if (!value) {
      continue;
    }

    const formatted = preventWidows(value);
    if (formatted !== value) {
      element.setAttribute(attribute, formatted);
    }
  }
}

function processNode(root) {
  if (!root) {
    return;
  }

  if (root.nodeType === Node.TEXT_NODE) {
    processTextNode(root);
    return;
  }

  if (root.nodeType !== Node.ELEMENT_NODE) {
    return;
  }

  const element = root;
  if (shouldSkipElement(element)) {
    return;
  }

  processAttributes(element);

  const walker = document.createTreeWalker(
    element,
    NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT
  );

  let current = walker.currentNode;
  while (current) {
    if (current.nodeType === Node.TEXT_NODE) {
      processTextNode(current);
    } else {
      processAttributes(current);
    }

    current = walker.nextNode();
  }
}

export function installTypography(root) {
  processNode(root);

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "characterData") {
        processTextNode(mutation.target);
        continue;
      }

      if (mutation.type === "attributes") {
        processAttributes(mutation.target);
        continue;
      }

      mutation.addedNodes.forEach((node) => processNode(node));
    }
  });

  observer.observe(root, {
    subtree: true,
    childList: true,
    characterData: true,
    attributes: true,
    attributeFilter: ATTRIBUTE_NAMES,
  });

  return observer;
}
