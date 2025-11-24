import '@testing-library/jest-dom';
import { vi } from 'vitest';

vi.stubGlobal('alert', vi.fn());
vi.stubGlobal('confirm', vi.fn(() => true));
