/*
 * ListItem — mirrors ListItem.kt.
 * MinHeight 60, MinWidth 360, shape r=16, bg=fillLight.
 * Kotlin default colors (defaultListItemColors):
 *   container=fillLight, headline=labelPrimary, supporting=labelTertiary,
 *   leading/trailing=Unspecified (inherits content color -> labelPrimary).
 */
import { SuiElement, define, emit, Dimension, themeColor } from './base.js';

export class SuiListItem extends SuiElement {
  static get observedAttributes() {
    return [
      'headline',
      'supporting',
      'leading-icon',
      'trailing-icon',
      'disabled',
      'container-color',
      'headline-color',
      'supporting-color',
    ];
  }
  render() {
    const disabled = this.bool('disabled');
    const leading = this.attr('leading-icon');
    const trailing = this.attr('trailing-icon');
    const supporting = this.attr('supporting');
    const bg = this.attr('container-color', themeColor('fillLight'));
    const headC = this.attr('headline-color', themeColor('labelPrimary'));
    const supC = this.attr('supporting-color', themeColor('labelTertiary'));
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:flex; }
        .item { display:flex; align-items:center; min-height:60px; min-width:360px; width:100%;
          padding:16px 4px 16px 16px; border-radius:${Dimension.RadiusLarge}px; background:${bg};
          cursor:pointer; box-sizing:border-box; transition:background-color .12s ease;
          color:${headC}; position:relative; overflow:hidden; }
        .item.sui-disabled { opacity: var(--sui-disable-alpha, 0.4); pointer-events: none; }
        .item::after { content:""; position:absolute; inset:0; background:transparent; transition:background-color .12s; pointer-events:none; }
        .item:hover::after { background: var(--sui-lighten-hover, rgba(255,255,255,0.12)); }
        .lead { margin-right:12px; display:inline-flex; align-items:center; font-size:22px; }
        .text { flex:1; min-width:0; position:relative; z-index:1; }
        .headline { color:${headC}; font-size:16px; line-height:20px; font-weight:600; }
        .support { color:${supC}; font-size:14px; line-height:18px; font-weight:500; margin-top:4px; }
        .trail { margin-left:16px; margin-right:8px; display:inline-flex; align-items:center; color:${supC}; position:relative; z-index:1; }
      </style>
      <div class="item ${disabled ? 'sui-disabled' : ''}">
        ${leading ? `<span class="lead">${leading}</span>` : ''}
        <div class="text">
          <div class="headline"><slot name="headline">${this.attr('headline', 'Headline')}</slot></div>
          ${supporting ? `<div class="support">${supporting}</div>` : ''}
        </div>
        ${trailing ? `<span class="trail">${trailing}</span>` : `<slot name="trailing"></slot>`}
      </div>`;
    this.shadowRoot.querySelector('.item').addEventListener('click', () => {
      if (!disabled) emit(this, 'click-action', {});
    });
  }
}
define('sui-list-item', SuiListItem);
