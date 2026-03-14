'use client'

import { useState, useRef } from 'react'
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  TrashIcon,
  EyeIcon 
} from '@heroicons/react/24/outline'

interface Document {
  id: number
  filename: string
  content_type: string
  file_size: number
  extracted_text?: string
  structured_data?: any
  created_at: Date
  parsing_success: boolean
}

export default function DocumentUpload() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)

    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await fetch('/api/upload/upload', {
          method: 'POST',
          body: formData
        })

        const result = await response.json()

        if (response.ok) {
          const newDoc: Document = {
            id: result.document_id,
            filename: result.filename,
            content_type: file.type,
            file_size: result.file_size,
            extracted_text: result.extracted_text,
            structured_data: result.structured_data,
            created_at: new Date(),
            parsing_success: result.parsing_success
          }

          setDocuments(prev => [newDoc, ...prev])
        } else {
          console.error('Upload failed:', result.error)
        }
      } catch (error) {
        console.error('Upload error:', error)
      }
    }

    setUploading(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDeleteDoc = async (docId: number) => {
    try {
      const response = await fetch(`/api/upload/document/${docId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.id !== docId))
        if (selectedDoc?.id === docId) {
          setSelectedDoc(null)
        }
      }
    } catch (error) {
      console.error('Delete error:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (contentType: string) => {
    if (contentType.includes('pdf')) return '📄'
    if (contentType.includes('image')) return '🖼️'
    if (contentType.includes('text')) return '📝'
    return '📄'
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="card">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="btn-primary">Choose Files</span>
              <input
                ref={fileInputRef}
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
            <p className="mt-2 text-sm text-gray-600">
              or drag and drop PDFs or images here
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Supported formats: PDF, JPG, PNG, BMP, TIFF (Max 10MB)
            </p>
          </div>
          {uploading && (
            <div className="mt-4">
              <div className="inline-flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm text-gray-600">Uploading...</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Documents List */}
      {documents.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Documents</h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getFileIcon(doc.content_type)}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>•</span>
                      <span>{doc.created_at.toLocaleDateString()}</span>
                      <span>•</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        doc.parsing_success 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {doc.parsing_success ? 'Parsed' : 'Failed'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSelectedDoc(doc)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteDoc(doc.id)}
                    className="p-2 text-red-600 hover:text-red-900 hover:bg-red-100 rounded"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Details Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Document Details
                  </h2>
                  <p className="text-gray-600">{selectedDoc.filename}</p>
                </div>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                {/* Document Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">File Size</h3>
                    <p className="text-gray-600">{formatFileSize(selectedDoc.file_size)}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">Content Type</h3>
                    <p className="text-gray-600">{selectedDoc.content_type}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">Upload Date</h3>
                    <p className="text-gray-600">{selectedDoc.created_at.toLocaleString()}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">Parsing Status</h3>
                    <p className={`font-medium ${
                      selectedDoc.parsing_success ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {selectedDoc.parsing_success ? 'Success' : 'Failed'}
                    </p>
                  </div>
                </div>

                {/* Extracted Text */}
                {selectedDoc.extracted_text && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Extracted Text</h3>
                    <div className="bg-gray-50 p-4 rounded max-h-64 overflow-y-auto">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {selectedDoc.extracted_text}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Structured Data */}
                {selectedDoc.structured_data && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Structured Information</h3>
                    <div className="bg-gray-50 p-4 rounded max-h-64 overflow-y-auto">
                      <div className="space-y-2">
                        {Object.entries(selectedDoc.structured_data).map(([key, value]) => (
                          <div key={key}>
                            <h4 className="font-medium text-gray-800 capitalize">{key}</h4>
                            {Array.isArray(value) ? (
                              <ul className="list-disc list-inside text-sm text-gray-600 ml-2">
                                {value.map((item, index) => (
                                  <li key={index}>{item}</li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-sm text-gray-600 ml-2">{String(value)}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {documents.length === 0 && !uploading && (
        <div className="text-center py-12">
          <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mt-4 mb-2">No documents uploaded</h3>
          <p className="text-gray-600">
            Upload documents to extract information and use them in your applications.
          </p>
        </div>
      )}
    </div>
  )
}
