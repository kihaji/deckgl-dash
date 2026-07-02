import { describe, it, expect } from 'vitest';
import { applyLayerOrder } from '../layerOrder';

describe('applyLayerOrder', () => {
    const configs = [{ id: 'a' }, { id: 'b' }, { id: 'c' }];

    it('reorders configs to match the order array (bottom to top)', () => {
        expect(applyLayerOrder(configs, ['c', 'a', 'b']).map(c => c.id)).toEqual(['c', 'a', 'b']);
    });

    it('appends unmentioned layers at the top, preserving relative order', () => {
        expect(applyLayerOrder(configs, ['b']).map(c => c.id)).toEqual(['b', 'a', 'c']);
    });

    it('ignores unknown ids in the order array', () => {
        expect(applyLayerOrder(configs, ['nope', 'c']).map(c => c.id)).toEqual(['c', 'a', 'b']);
    });

    it('drops configs without ids', () => {
        expect(applyLayerOrder([{ id: 'a' }, { noId: true }], ['a']).map(c => c.id)).toEqual(['a']);
    });

    it('handles empty inputs', () => {
        expect(applyLayerOrder([], [])).toEqual([]);
        expect(applyLayerOrder(configs, []).map(c => c.id)).toEqual(['a', 'b', 'c']);
    });
});
