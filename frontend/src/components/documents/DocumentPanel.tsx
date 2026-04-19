import { useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, Upload, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { useDocMindStore } from "../../store";

export function DocumentPanel() {
  const { documents, uploadStatus, uploadError, upload, fetchDocuments } = useDocMindStore();

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

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-800">Documents</h2>
        <p className="text-xs text-gray-400 mt-1">Upload PDFs, TXT, or Markdown files</p>
      </div>

      <div className="px-6 py-4">
        {/* Dropzone */}
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
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
          Ingested ({documents.length})
        </p>
        {documents.length === 0 ? (
          <p className="text-sm text-gray-400">No documents yet.</p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li key={doc} className="flex items-center gap-2 text-sm text-gray-700 bg-gray-50 rounded-lg px-3 py-2">
                <FileText size={14} className="text-blue-500 shrink-0" />
                <span className="truncate">{doc.split("/").pop()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
