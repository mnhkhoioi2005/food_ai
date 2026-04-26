import { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Camera, Upload, X, Loader, CheckCircle, AlertCircle, RefreshCw, Image as ImageIcon } from 'lucide-react';
import { recognitionAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import FoodCard from '../components/FoodCard';
import { Link } from 'react-router-dom';

const BBOX_COLORS = [
  '#22c55e', // green
  '#3b82f6', // blue
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
];

const RecognitionPage = () => {
  const [mode, setMode] = useState('upload'); // 'upload' | 'camera'
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const imgRef = useRef(null);
  const { isAuthenticated } = useAuth();

  // Handle file upload
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('File quá lớn. Vui lòng chọn file nhỏ hơn 10MB.');
        return;
      }
      
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  // Capture from webcam
  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      // Convert base64 to blob
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
          setImage(file);
          setPreview(imageSrc);
          setResult(null);
          setError(null);
        });
    }
  }, [webcamRef]);

  // Submit for recognition
  const handleRecognize = async () => {
    if (!image) {
      setError('Vui lòng chọn hoặc chụp ảnh');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = mode === 'camera'
        ? await recognitionAPI.cameraCapture(image)
        : await recognitionAPI.uploadImage(image);
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  // Reset state
  const handleReset = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Vẽ bounding boxes lên canvas khi có kết quả
  useEffect(() => {
    if (!result || !imgRef.current || !canvasRef.current) return;
    const predictions = result.predictions || [];
    const imgW = result.image_width;
    const imgH = result.image_height;
    if (!imgW || !imgH) return;

    const img = imgRef.current;
    const canvas = canvasRef.current;

    const draw = () => {
      const displayW = img.clientWidth;
      const displayH = img.clientHeight;
      canvas.width = displayW;
      canvas.height = displayH;

      const scaleX = displayW / imgW;
      const scaleY = displayH / imgH;

      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, displayW, displayH);

      predictions.forEach((pred, idx) => {
        const bbox = pred.bbox;
        if (!bbox || bbox.length < 4) return;

        const [x1, y1, x2, y2] = bbox;
        const rx = x1 * scaleX;
        const ry = y1 * scaleY;
        const rw = (x2 - x1) * scaleX;
        const rh = (y2 - y1) * scaleY;

        const color = BBOX_COLORS[idx % BBOX_COLORS.length];

        // Vẽ viền box
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(rx, ry, rw, rh);

        // Vẽ nền cho label
        const label = `${pred.food_name || pred.food_name_en || '???'}  ${(pred.confidence * 100).toFixed(1)}%`;
        ctx.font = 'bold 14px sans-serif';
        const textW = ctx.measureText(label).width;
        const textH = 22;
        const labelY = ry > textH + 4 ? ry - textH - 4 : ry;

        ctx.fillStyle = color;
        ctx.fillRect(rx, labelY, textW + 12, textH);

        // Vẽ text
        ctx.fillStyle = '#fff';
        ctx.fillText(label, rx + 6, labelY + 16);
      });
    };

    // Đợi ảnh load xong rồi vẽ
    if (img.complete) {
      draw();
    } else {
      img.onload = draw;
    }

    // Vẽ lại khi resize cửa sổ
    window.addEventListener('resize', draw);
    return () => window.removeEventListener('resize', draw);
  }, [result]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
          <Camera className="inline-block mr-2 text-primary-500" />
          Nhận diện món ăn
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Chụp ảnh hoặc tải lên hình ảnh món ăn, AI sẽ nhận diện và cung cấp thông tin chi tiết
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          {/* Mode Toggle */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
            <button
              onClick={() => { setMode('upload'); handleReset(); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all
                ${mode === 'upload' ? 'bg-white shadow text-primary-600' : 'text-gray-600'}`}
            >
              <Upload size={18} />
              Tải ảnh lên
            </button>
            <button
              onClick={() => { setMode('camera'); handleReset(); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all
                ${mode === 'camera' ? 'bg-white shadow text-primary-600' : 'text-gray-600'}`}
            >
              <Camera size={18} />
              Chụp ảnh
            </button>
          </div>

          {/* Upload Mode */}
          {mode === 'upload' && !preview && (
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-all"
            >
              <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                Kéo thả ảnh vào đây hoặc click để chọn
              </p>
              <p className="text-sm text-gray-400">
                Hỗ trợ: JPG, PNG, WEBP (tối đa 10MB)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          )}

          {/* Camera Mode */}
          {mode === 'camera' && !preview && (
            <div className="relative">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  width: 640,
                  height: 480,
                  facingMode: "environment"
                }}
                onUserMedia={() => setCameraReady(true)}
                onUserMediaError={() => setError('Không thể truy cập camera. Vui lòng cấp quyền.')}
                className="w-full rounded-2xl"
              />
              {cameraReady && (
                <button
                  onClick={capture}
                  className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
                >
                  <div className="w-12 h-12 bg-primary-500 rounded-full" />
                </button>
              )}
            </div>
          )}

          {/* Preview */}
          {preview && (
            <div className="relative">
              <img 
                ref={imgRef}
                src={preview} 
                alt="Preview" 
                className="w-full rounded-2xl"
              />
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none rounded-2xl"
              />
              <button
                onClick={handleReset}
                className="absolute top-3 right-3 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-100 transition-all z-10"
              >
                <X size={20} />
              </button>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-3">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* Action Buttons */}
          {preview && !result && (
            <div className="mt-6 flex gap-4">
              <button
                onClick={handleReset}
                className="flex-1 btn-secondary flex items-center justify-center gap-2"
              >
                <RefreshCw size={18} />
                Chọn ảnh khác
              </button>
              <button
                onClick={handleRecognize}
                disabled={loading}
                className="flex-1 btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader className="animate-spin" size={18} />
                    Đang xử lý...
                  </>
                ) : (
                  <>
                    <Camera size={18} />
                    Nhận diện
                  </>
                )}
              </button>
            </div>
          )}

          {/* Auth notice */}
          {!isAuthenticated && (
            <div className="mt-4 p-4 bg-blue-50 text-blue-600 rounded-xl text-sm">
              💡 <Link to="/login" className="underline font-medium">Đăng nhập</Link> để lưu lịch sử nhận diện và nhận gợi ý cá nhân hóa.
            </div>
          )}
        </div>

        {/* Result Section */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Kết quả nhận diện
          </h2>

          {!result && !loading && (
            <div className="text-center py-12 text-gray-400">
              <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Kết quả sẽ hiển thị ở đây</p>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <Loader className="w-12 h-12 mx-auto mb-4 text-primary-500 animate-spin" />
              <p className="text-gray-600">Đang phân tích hình ảnh...</p>
            </div>
          )}

          {result && (
            <div className="space-y-6 animate-fadeIn">
              {/* Main prediction */}
              {result.predictions && result.predictions.length > 0 ? (
              <div className="p-4 bg-green-50 rounded-xl">
                <div className="flex items-center gap-2 text-green-600 mb-2">
                  <CheckCircle size={20} />
                  <span className="font-medium">Nhận diện thành công!</span>
                </div>
                <p className="text-2xl font-bold text-gray-800 mb-1">
                  {result.predictions?.[0]?.food_name || result.top_prediction?.food_name || 'Không nhận diện được'}
                </p>
                <p className="text-gray-500">
                  Độ tin cậy: {((result.predictions?.[0]?.confidence || result.top_prediction?.confidence || 0) * 100).toFixed(1)}%
                </p>
              </div>
              ) : (
              <div className="p-4 bg-yellow-50 rounded-xl">
                <div className="flex items-center gap-2 text-yellow-600 mb-2">
                  <AlertCircle size={20} />
                  <span className="font-medium">Không nhận diện được</span>
                </div>
                <p className="text-gray-600 text-sm">
                  AI không tìm thấy món ăn Việt Nam trong ảnh này. Hãy thử ảnh khác hoặc chụp gần hơn.
                </p>
              </div>
              )}

              {/* Top predictions */}
              {result.predictions && result.predictions.length > 1 && (
                <div>
                  <h3 className="font-medium text-gray-700 mb-3">Các kết quả khác:</h3>
                  <div className="space-y-2">
                    {result.predictions.slice(1, 5).map((pred, idx) => (
                      <div 
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                      >
                        <span className="text-gray-700">{pred.food_name}</span>
                        <span className="text-sm text-gray-500">
                          {(pred.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Food details */}
              {result.food && (
                <div>
                  <h3 className="font-medium text-gray-700 mb-3">Thông tin món ăn:</h3>
                  <FoodCard food={result.food} />
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-4">
                <button
                  onClick={handleReset}
                  className="flex-1 btn-secondary flex items-center justify-center gap-2"
                >
                  <RefreshCw size={18} />
                  Nhận diện khác
                </button>
                {(result.predictions?.[0]?.food_id || result.top_prediction?.food_id) && (
                  <Link
                    to={`/food/${result.predictions?.[0]?.food_id || result.top_prediction?.food_id}`}
                    className="flex-1 btn-primary flex items-center justify-center gap-2"
                  >
                    Xem chi tiết
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="mt-12 bg-primary-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          💡 Mẹo để có kết quả tốt nhất
        </h3>
        <ul className="grid md:grid-cols-2 gap-4 text-gray-600">
          <li className="flex items-start gap-2">
            <CheckCircle className="text-primary-500 mt-0.5 flex-shrink-0" size={18} />
            <span>Chụp ảnh rõ nét, đủ sáng</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="text-primary-500 mt-0.5 flex-shrink-0" size={18} />
            <span>Để món ăn ở trung tâm khung hình</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="text-primary-500 mt-0.5 flex-shrink-0" size={18} />
            <span>Tránh che khuất món ăn</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="text-primary-500 mt-0.5 flex-shrink-0" size={18} />
            <span>Chụp từ góc nhìn phía trên</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default RecognitionPage;
