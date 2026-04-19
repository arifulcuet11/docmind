import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, Upload, Loader2, CheckCircle, AlertCircle, Trash2 } from "lucide-react";
import { useDocMindStore } from "../../store";

export function DocumentPanel() {
  const {
    documents,
    selectedSources,
    uploadStatus,
    uploadError,
    upload,
    fetchDocuments,
    deleteDoc,
    toggleSource,
    selectAllSources,
    clearSourceSelection,
  } = useDocMindStore();

  const [deletingFile, setDeletingFile] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles[0]) upload(acceptedFiles[0]);
    },
    [upload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "text/plain": [".txt"], "text/markdown": [".md"] },
    multiple: false,
  });

  const handleDelete = async (doc: string) => {
    const filename = doc.split("/").pop() || doc;
    const confirmed = window.confirm(`Delete "${filename}"?`);
    if (!confirmed) return;
    setDeletingFile(filename);
    await deleteDoc(filename);
    setDeletingFile(null);
  };

  const allSelected = documents.length > 0 && selectedSources.length === documents.length;
  const noneSelected = selectedSources.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-800">Documents</h2>
        <p className="text-xs text-gray-400 mt-1">Upload PDFs, TXT, or Markdown files</p>
      </div>

      {/* Dropzone */}
      <div className="px-6 py-4">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
            isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400"
          }`}
        >
          <input {...getInputProps()} />
          <Upload size={24} className="mx-auto text-gray-400 mb-2" />
          <p className="text-sm text-gray-500">
            {isDragActive ? "Drop file here…" : "Drag & drop or click to upload"}
          </p>
          <p className="text-xs text-gray-400 mt-1">PDF, TXT, MD — max 50MB</p>
        </div>

        {/* Upload status */}
        {uploadStatus === "uploading" && (
          <div className="flex items-center gap-2 mt-3 text-sm text-blue-600">
            <Loader2 size={14} className="animate-spin" /> Uploading & ingesting…
          </div>
        )}
        {uploadStatus === "success" && (
          <div className="flex items-center gap-2 mt-3 text-sm text-green-600">
            <CheckCircle size={14} /> Document ingested successfully!
          </div>
        )}
        {uploadStatus === "error" && (
          <div className="flex items-center gap-2 mt-3 text-sm text-red-500">
            <AlertCircle size={14} /> {uploadError || "Upload failed"}
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-6">

        {/* Header row — count + select all/none */}
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Ingested ({documents.length})
          </p>
          {documents.length > 0 && (
            <div className="flex gap-2">
              <button
                onClick={selectAllSources}
                className="text-xs text-blue-500 hover:underline"
              >
                All
              </button>
              <span className="text-xs text-gray-300">|</span>
              <button
                onClick={clearSourceSelection}
                className="text-xs text-gray-400 hover:underline"
              >
                None
              </button>
            </div>
          )}
        </div>

        {/* Filter info */}
        {documents.length > 0 && (
          <p className="text-xs text-gray-400 mb-3">
            {noneSelected
              ? "Searching all documents"
              : `Searching ${selectedSources.length} of ${documents.length} document${selectedSources.length > 1 ? "s" : ""}`}
          </p>
        )}

        {documents.length === 0 ? (
          <p className="text-sm text-gray-400">No documents yet.</p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => {
              const filename = doc.split("/").pop() || doc;
              const isDeleting = deletingFile === filename;
              const isSelected = selectedSources.includes(doc);

              return (
                <li
                  key={doc}
                  className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2 group transition-colors ${
                    isSelected
                      ? "bg-blue-50 border border-blue-200 text-blue-800"
                      : "bg-gray-50 text-gray-700"
                  }`}
                >
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleSource(doc)}
                    className="rounded border-gray-300 text-blue-600 shrink-0 cursor-pointer"
                  />

                  {/* File icon */}
                  <FileText
                    size={14}
                    className={isSelected ? "text-blue-500 shrink-0" : "text-gray-400 shrink-0"}
                  />

                  {/* Filename */}
                  <span className="truncate flex-1 cursor-pointer" title={filename} onClick={() => toggleSource(doc)}>
                    {filename}
                  </span>

                  {/* Delete button */}
                  {isDeleting ? (
                    <Loader2 size={14} className="animate-spin text-gray-400 shrink-0" />
                  ) : (
                    <button
                      onClick={() => handleDelete(doc)}
                      className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all shrink-0"
                      title="Delete document"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}