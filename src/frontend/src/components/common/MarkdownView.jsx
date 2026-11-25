import ReactMarkdown from 'react-markdown';

// Renders Markdown ONLY. Raw HTML and scripts inside model output are never
// executed (react-markdown skips raw HTML by default); dangerouslySetInnerHTML
// is not used anywhere in this application.
const MarkdownView = ({ content }) => (
  <div className="space-y-2 text-sm leading-6 [&_h1]:text-lg [&_h1]:font-bold [&_h2]:text-base [&_h2]:font-semibold [&_h3]:font-semibold [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_a]:text-emerald-700 [&_a]:underline [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1 [&_code]:text-xs [&_pre]:overflow-auto [&_pre]:rounded [&_pre]:bg-slate-100 [&_pre]:p-2 [&_blockquote]:border-l-4 [&_blockquote]:border-slate-300 [&_blockquote]:pl-3 [&_table]:w-full [&_th]:border [&_th]:px-2 [&_td]:border [&_td]:px-2">
    <ReactMarkdown>{content || ''}</ReactMarkdown>
  </div>
);

export default MarkdownView;
