import React, { useState, useEffect } from 'react';

const DebugInfo = ({ user }) => {
  const [telegramData, setTelegramData] = useState(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      setTelegramData({
        version: tg.version,
        platform: tg.platform,
        initDataUnsafe: tg.initDataUnsafe,
        initData: tg.initData ? tg.initData.substring(0, 100) + '...' : null,
        colorScheme: tg.colorScheme,
        viewportHeight: tg.viewportHeight,
        isExpanded: tg.isExpanded,
      });
    }
  }, []);

  if (!show) {
    return (
      <button
        onClick={() => setShow(true)}
        className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-full shadow-lg hover:bg-gray-700 text-sm z-50"
      >
        🐛 Debug
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">🐛 Отладочная информация</h2>
          <button
            onClick={() => setShow(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {/* User Data */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">👤 User (from App state):</h3>
          <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>

        {/* Telegram WebApp Data */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">📱 Telegram WebApp:</h3>
          {telegramData ? (
            <div className="space-y-2">
              <div className="bg-gray-100 p-3 rounded">
                <p className="text-sm"><strong>Version:</strong> {telegramData.version}</p>
                <p className="text-sm"><strong>Platform:</strong> {telegramData.platform}</p>
                <p className="text-sm"><strong>Color Scheme:</strong> {telegramData.colorScheme}</p>
                <p className="text-sm"><strong>Expanded:</strong> {telegramData.isExpanded ? 'Yes' : 'No'}</p>
              </div>

              <div>
                <p className="font-semibold text-sm mb-1">initDataUnsafe:</p>
                <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                  {JSON.stringify(telegramData.initDataUnsafe, null, 2)}
                </pre>
              </div>

              <div>
                <p className="font-semibold text-sm mb-1">initData (truncated):</p>
                <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto break-all">
                  {telegramData.initData || 'null'}
                </pre>
              </div>
            </div>
          ) : (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              ❌ Telegram WebApp не доступен
            </div>
          )}
        </div>

        {/* Backend URL */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">🔗 Backend URL:</h3>
          <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
            {process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'Not set'}
          </pre>
        </div>

        {/* Test Backend */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">🧪 Backend Test:</h3>
          <button
            onClick={async () => {
              try {
                const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
                const response = await fetch(`${backendUrl}/api/health`);
                const data = await response.json();
                alert(`✅ Backend OK\n${JSON.stringify(data, null, 2)}`);
              } catch (error) {
                alert(`❌ Backend Error\n${error.message}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Test /api/health
          </button>
        </div>

        {/* Instructions */}
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <h3 className="font-semibold text-sm mb-2">📋 Диагностика:</h3>
          <ul className="text-xs space-y-1">
            <li>• <strong>User is null:</strong> Проверьте Telegram initDataUnsafe.user</li>
            <li>• <strong>initDataUnsafe пустой:</strong> URL в BotFather неправильный</li>
            <li>• <strong>initDataUnsafe есть, но User null:</strong> Backend не аутентифицирует</li>
            <li>• <strong>Backend Test Error:</strong> CORS или URL неправильный</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DebugInfo;
