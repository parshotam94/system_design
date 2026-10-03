/**
 * Reusable CodeBlock Component with C++ Syntax Highlighting & Line Numbers
 */

const CodeBlock = {
  // Simple, fast C++ syntax highlighter
  highlightCpp(rawCode) {
    let html = rawCode
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Preprocessors (#include <...>, #pragma, #define)
    html = html.replace(/(#include\s+(&lt;.*?&gt;|&quot;.*?&quot;)|#pragma\s+once|#define\s+\w+)/g, '<span class="token-preprocessor">$1</span>');

    // Single-line comments
    html = html.replace(/(\/\/.*$)/gm, '<span class="token-comment">$1</span>');

    // Strings
    html = html.replace(/(".*?")/g, '<span class="token-string">$1</span>');

    // Keywords
    const keywords = [
      'class', 'struct', 'public', 'private', 'protected', 'virtual', 'override',
      'final', 'explicit', 'const', 'constexpr', 'static', 'nullptr', 'return',
      'if', 'else', 'for', 'while', 'new', 'delete', 'friend', 'namespace',
      'using', 'typename', 'template', 'auto', 'enum', 'noexcept', 'mutable'
    ];
    const kwRegex = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');
    html = html.replace(kwRegex, '<span class="token-keyword">$1</span>');

    // Core Types
    const types = [
      'int', 'void', 'bool', 'double', 'float', 'char', 'size_t',
      'std::string', 'std::vector', 'std::unique_ptr', 'std::shared_ptr',
      'std::weak_ptr', 'std::make_unique', 'std::make_shared',
      'std::mutex', 'std::lock_guard', 'std::unique_lock', 'std::shared_mutex',
      'std::atomic', 'std::condition_variable', 'std::optional', 'std::move'
    ];
    const typeRegex = new RegExp(`\\b(${types.join('|').replace(/::/g, '::')})\\b`, 'g');
    html = html.replace(typeRegex, '<span class="token-type">$1</span>');

    return html;
  },

  render(containerEl, filename, rawCode, options = {}) {
    const lines = rawCode.trim().split('\n');
    const lineCount = lines.length;
    
    // Generate line numbers
    const lineNumsHtml = Array.from({ length: lineCount }, (_, i) => `<div>${i + 1}</div>`).join('');
    const highlightedContent = this.highlightCpp(rawCode);

    const blockHtml = `
      <div class="code-container">
        <div class="code-header">
          <div class="code-header-left">
            <span class="code-filename">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              ${filename || 'example.cpp'}
            </span>
            <span class="code-lang-tag">C++20</span>
          </div>
          <div class="code-actions">
            <button class="code-btn btn-copy" title="Copy code">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
              Copy
            </button>
          </div>
        </div>
        <div class="code-body">
          <div class="code-line-numbers">${lineNumsHtml}</div>
          <div class="code-content">${highlightedContent}</div>
        </div>
      </div>
    `;

    containerEl.innerHTML = blockHtml;

    // Attach copy event listener
    const copyBtn = containerEl.querySelector('.btn-copy');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(rawCode).then(() => {
          copyBtn.innerHTML = `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Copied!
          `;
          if (window.showToast) window.showToast('C++ code snippet copied to clipboard!');
          setTimeout(() => {
            copyBtn.innerHTML = `
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
              Copy
            `;
          }, 2000);
        });
      });
    }
  }
};

window.CodeBlock = CodeBlock;
