'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { SUPPORTED_LOCALES } from '@/lib/i18n';

/**
 * Language Switcher Component
 * Allows users to switch between supported languages
 */
export default function LanguageSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  function switchLocale(newLocale: string) {
    const segments = pathname.split('/');
    segments[1] = newLocale;
    router.push(segments.join('/'));
  }

  return (
    <div className="flex gap-2 items-center">
      <span className="text-sm text-gray-600 mr-2">Language:</span>
      {Object.entries(SUPPORTED_LOCALES).map(([code, info]) => (
        <button
          key={code}
          onClick={() => switchLocale(code)}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            locale === code
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          title={info.nativeName}
        >
          <span className="mr-1">{info.flag}</span>
          <span className="hidden sm:inline">{code}</span>
        </button>
      ))}
    </div>
  );
}
