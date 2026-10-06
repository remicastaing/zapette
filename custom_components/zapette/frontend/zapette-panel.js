var Z=globalThis,J=Z.ShadowRoot&&(Z.ShadyCSS===void 0||Z.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,te=Symbol(),ke=new WeakMap,L=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==te)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(J&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=ke.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&ke.set(t,e))}return e}toString(){return this.cssText}},ze=r=>new L(typeof r=="string"?r:r+"",void 0,te),$=(r,...e)=>{let t=r.length===1?r[0]:e.reduce((s,a,i)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(a)+r[i+1],r[0]);return new L(t,r,te)},Ae=(r,e)=>{if(J)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),a=Z.litNonce;a!==void 0&&s.setAttribute("nonce",a),s.textContent=t.cssText,r.appendChild(s)}},se=J?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return ze(t)})(r):r;var{is:at,defineProperty:it,getOwnPropertyDescriptor:nt,getOwnPropertyNames:rt,getOwnPropertySymbols:ot,getPrototypeOf:lt}=Object,X=globalThis,Se=X.trustedTypes,dt=Se?Se.emptyScript:"",pt=X.reactiveElementPolyfillSupport,O=(r,e)=>r,ae={toAttribute(r,e){switch(e){case Boolean:r=r?dt:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},Ce=(r,e)=>!at(r,e),Ee={attribute:!0,type:String,converter:ae,reflect:!1,useDefault:!1,hasChanged:Ce};Symbol.metadata??=Symbol("metadata"),X.litPropertyMetadata??=new WeakMap;var k=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=Ee){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),a=this.getPropertyDescriptor(e,s,t);a!==void 0&&it(this.prototype,e,a)}}static getPropertyDescriptor(e,t,s){let{get:a,set:i}=nt(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:a,set(n){let l=a?.call(this);i?.call(this,n),this.requestUpdate(e,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??Ee}static _$Ei(){if(this.hasOwnProperty(O("elementProperties")))return;let e=lt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(O("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(O("properties"))){let t=this.properties,s=[...rt(t),...ot(t)];for(let a of s)this.createProperty(a,t[a])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,a]of t)this.elementProperties.set(s,a)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let a=this._$Eu(t,s);a!==void 0&&this._$Eh.set(a,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let a of s)t.unshift(se(a))}else e!==void 0&&t.push(se(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ae(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),a=this.constructor._$Eu(e,s);if(a!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:ae).toAttribute(t,s.type);this._$Em=e,i==null?this.removeAttribute(a):this.setAttribute(a,i),this._$Em=null}}_$AK(e,t){let s=this.constructor,a=s._$Eh.get(e);if(a!==void 0&&this._$Em!==a){let i=s.getPropertyOptions(a),n=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:ae;this._$Em=a;let l=n.fromAttribute(t,i.type);this[a]=l??this._$Ej?.get(a)??l,this._$Em=null}}requestUpdate(e,t,s,a=!1,i){if(e!==void 0){let n=this.constructor;if(a===!1&&(i=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??Ce)(i,t)||s.useDefault&&s.reflect&&i===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:a,wrapped:i},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),i!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),a===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[a,i]of this._$Ep)this[a]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[a,i]of s){let{wrapped:n}=i,l=this[a];n!==!0||this._$AL.has(a)||l===void 0||this.C(a,void 0,i,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};k.elementStyles=[],k.shadowRootOptions={mode:"open"},k[O("elementProperties")]=new Map,k[O("finalized")]=new Map,pt?.({ReactiveElement:k}),(X.reactiveElementVersions??=[]).push("2.1.2");var pe=globalThis,Te=r=>r,G=pe.trustedTypes,Me=G?G.createPolicy("lit-html",{createHTML:r=>r}):void 0,Re="$lit$",A=`lit$${Math.random().toFixed(9).slice(2)}$`,Le="?"+A,ct=`<${Le}>`,M=document,U=()=>M.createComment(""),V=r=>r===null||typeof r!="object"&&typeof r!="function",ce=Array.isArray,ut=r=>ce(r)||typeof r?.[Symbol.iterator]=="function",ie=`[ 	
\f\r]`,j=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,qe=/-->/g,Pe=/>/g,C=RegExp(`>|${ie}(?:([^\\s"'>=/]+)(${ie}*=${ie}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),De=/'/g,Ne=/"/g,Oe=/^(?:script|style|textarea|title)$/i,ue=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),o=ue(1),w=ue(2),Rt=ue(3),q=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),Ie=new WeakMap,T=M.createTreeWalker(M,129);function je(r,e){if(!ce(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return Me!==void 0?Me.createHTML(e):e}var ht=(r,e)=>{let t=r.length-1,s=[],a,i=e===2?"<svg>":e===3?"<math>":"",n=j;for(let l=0;l<t;l++){let d=r[l],c,h,_=-1,u=0;for(;u<d.length&&(n.lastIndex=u,h=n.exec(d),h!==null);)u=n.lastIndex,n===j?h[1]==="!--"?n=qe:h[1]!==void 0?n=Pe:h[2]!==void 0?(Oe.test(h[2])&&(a=RegExp("</"+h[2],"g")),n=C):h[3]!==void 0&&(n=C):n===C?h[0]===">"?(n=a??j,_=-1):h[1]===void 0?_=-2:(_=n.lastIndex-h[2].length,c=h[1],n=h[3]===void 0?C:h[3]==='"'?Ne:De):n===Ne||n===De?n=C:n===qe||n===Pe?n=j:(n=C,a=void 0);let g=n===C&&r[l+1].startsWith("/>")?" ":"";i+=n===j?d+ct:_>=0?(s.push(c),d.slice(0,_)+Re+d.slice(_)+A+g):d+A+(_===-2?l:g)}return[je(r,i+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},H=class r{constructor({strings:e,_$litType$:t},s){let a;this.parts=[];let i=0,n=0,l=e.length-1,d=this.parts,[c,h]=ht(e,t);if(this.el=r.createElement(c,s),T.currentNode=this.el.content,t===2||t===3){let _=this.el.content.firstChild;_.replaceWith(..._.childNodes)}for(;(a=T.nextNode())!==null&&d.length<l;){if(a.nodeType===1){if(a.hasAttributes())for(let _ of a.getAttributeNames())if(_.endsWith(Re)){let u=h[n++],g=a.getAttribute(_).split(A),v=/([.?@])?(.*)/.exec(u);d.push({type:1,index:i,name:v[2],strings:g,ctor:v[1]==="."?re:v[1]==="?"?oe:v[1]==="@"?le:D}),a.removeAttribute(_)}else _.startsWith(A)&&(d.push({type:6,index:i}),a.removeAttribute(_));if(Oe.test(a.tagName)){let _=a.textContent.split(A),u=_.length-1;if(u>0){a.textContent=G?G.emptyScript:"";for(let g=0;g<u;g++)a.append(_[g],U()),T.nextNode(),d.push({type:2,index:++i});a.append(_[u],U())}}}else if(a.nodeType===8)if(a.data===Le)d.push({type:2,index:i});else{let _=-1;for(;(_=a.data.indexOf(A,_+1))!==-1;)d.push({type:7,index:i}),_+=A.length-1}i++}}static createElement(e,t){let s=M.createElement("template");return s.innerHTML=e,s}};function P(r,e,t=r,s){if(e===q)return e;let a=s!==void 0?t._$Co?.[s]:t._$Cl,i=V(e)?void 0:e._$litDirective$;return a?.constructor!==i&&(a?._$AO?.(!1),i===void 0?a=void 0:(a=new i(r),a._$AT(r,t,s)),s!==void 0?(t._$Co??=[])[s]=a:t._$Cl=a),a!==void 0&&(e=P(r,a._$AS(r,e.values),a,s)),e}var ne=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,a=(e?.creationScope??M).importNode(t,!0);T.currentNode=a;let i=T.nextNode(),n=0,l=0,d=s[0];for(;d!==void 0;){if(n===d.index){let c;d.type===2?c=new K(i,i.nextSibling,this,e):d.type===1?c=new d.ctor(i,d.name,d.strings,this,e):d.type===6&&(c=new de(i,this,e)),this._$AV.push(c),d=s[++l]}n!==d?.index&&(i=T.nextNode(),n++)}return T.currentNode=M,a}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},K=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,a){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=P(this,e,t),V(e)?e===p||e==null||e===""?(this._$AH!==p&&this._$AR(),this._$AH=p):e!==this._$AH&&e!==q&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):ut(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==p&&V(this._$AH)?this._$AA.nextSibling.data=e:this.T(M.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,a=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=H.createElement(je(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===a)this._$AH.p(t);else{let i=new ne(a,this),n=i.u(this.options);i.p(t),this.T(n),this._$AH=i}}_$AC(e){let t=Ie.get(e.strings);return t===void 0&&Ie.set(e.strings,t=new H(e)),t}k(e){ce(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,a=0;for(let i of e)a===t.length?t.push(s=new r(this.O(U()),this.O(U()),this,this.options)):s=t[a],s._$AI(i),a++;a<t.length&&(this._$AR(s&&s._$AB.nextSibling,a),t.length=a)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=Te(e).nextSibling;Te(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},D=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,a,i){this.type=1,this._$AH=p,this._$AN=void 0,this.element=e,this.name=t,this._$AM=a,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=p}_$AI(e,t=this,s,a){let i=this.strings,n=!1;if(i===void 0)e=P(this,e,t,0),n=!V(e)||e!==this._$AH&&e!==q,n&&(this._$AH=e);else{let l=e,d,c;for(e=i[0],d=0;d<i.length-1;d++)c=P(this,l[s+d],t,d),c===q&&(c=this._$AH[d]),n||=!V(c)||c!==this._$AH[d],c===p?e=p:e!==p&&(e+=(c??"")+i[d+1]),this._$AH[d]=c}n&&!a&&this.j(e)}j(e){e===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},re=class extends D{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===p?void 0:e}},oe=class extends D{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==p)}},le=class extends D{constructor(e,t,s,a,i){super(e,t,s,a,i),this.type=5}_$AI(e,t=this){if((e=P(this,e,t,0)??p)===q)return;let s=this._$AH,a=e===p&&s!==p||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,i=e!==p&&(s===p||a);a&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},de=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){P(this,e)}};var _t=pe.litHtmlPolyfillSupport;_t?.(H,K),(pe.litHtmlVersions??=[]).push("3.3.3");var Ue=(r,e,t)=>{let s=t?.renderBefore??e,a=s._$litPart$;if(a===void 0){let i=t?.renderBefore??null;s._$litPart$=a=new K(e.insertBefore(U(),i),i,void 0,t??{})}return a._$AI(r),a};var he=globalThis,y=class extends k{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ue(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return q}};y._$litElement$=!0,y.finalized=!0,he.litElementHydrateSupport?.({LitElement:y});var gt=he.litElementPolyfillSupport;gt?.({LitElement:y});(he.litElementVersions??=[]).push("4.2.2");var He=["mon","tue","wed","thu","fri","sat","sun"],S=[0,1,2,3,4,5,6],Ke=[0,1,2,3,4],We=[5,6],mt=4,ge=5,f=1440,Ve=["#1f9e8a","#d9732b","#7b61c9","#c2417a","#2f7fd1","#8a9a1f","#a0622d","#c99a16"],ft="#5f7389",yt="#9e9e9e",bt="#8d8d8d";function N(r){return typeof r=="number"?Ve[r%Ve.length]:{parent:ft,deleted:yt}[r]??bt}var _e=r=>String(r).padStart(2,"0"),m=r=>`${_e(Math.floor(r/60)%24)}:${_e(r%60)}`,b=r=>r%60?`${Math.floor(r/60)} h ${_e(r%60)}`:`${r/60} h`,me=r=>{if(!r)return null;let[e,t]=r.split(":").map(Number);return e*60+t},x=(r,e,t)=>Math.min(t,Math.max(e,r)),I=r=>structuredClone(r),W=r=>r.reduce((e,[t,s])=>e+s-t,0),Be=()=>(new Date().getDay()+6)%7;function vt(r){let e=[];for(let[t,s]of[...r].sort((a,i)=>a[0]-i[0])){let a=e.at(-1);a&&t<=a[1]?a[1]=Math.max(a[1],s):e.push([t,s])}return e}function B(r,e,t){let s=r.slots[e].length+1,a=vt([...r.slots[e],t]);return a.length>mt?{error:"max_slots",params:{day:e}}:(r.slots[e]=a,a.length<s?{info:"merged"}:null)}function Qe(r){let e=[],{quota:t,slots:s}=r;if(r.enabled||e.push({key:"disabled",params:{name:r.name}}),!S.some(a=>t[a]>0&&s[a].length))return e.push({key:"never",params:{name:r.name}}),e;for(let a of S){let i=W(s[a]);t[a]&&!s[a].length?e.push({key:"no_slot",params:{day:a}}):s[a].length&&!t[a]?e.push({key:"no_quota",params:{day:a}}):t[a]>i&&e.push({key:"exceeds",params:{day:a,quota:b(t[a]),slots:b(i)}})}return e}var E=(r,e,t)=>r>1?t:e,Ye={days:[["Lun","lundi"],["Mar","mardi"],["Mer","mercredi"],["Jeu","jeudi"],["Ven","vendredi"],["Sam","samedi"],["Dim","dimanche"]],grid:{hint_mouse:"Glissez dans une colonne pour cr\xE9er une plage, \xE9tirez ses bords pour l'ajuster, d\xE9placez-la d'un jour \xE0 l'autre.",hint_touch:"Touchez une colonne pour cr\xE9er une plage d'1 h, puis touchez-la pour l'ajuster.",fine:"Pas de 5 min",night:"Afficher la nuit",copy_day_aria:"Copier le {day} vers d'autres jours",quota_aria:"Quota du {day} : {value}. Modifier.",none_m:"aucun",none_f:"aucune",gauge_title:"Quota {quota} sur {total} de plages",gauge_none:"Aucune plage",slot_aria:"{Day}, de {start} \xE0 {end}. Entr\xE9e pour modifier, fl\xE8ches pour d\xE9placer, Suppr pour supprimer.",now:"Maintenant",slot_title:"Plage du {day}",start:"D\xE9but",end:"Fin",slot_note:"Pr\xE9cision \xE0 5 minutes. Fin \xE0 00:00 = minuit.",duplicate_on:"Dupliquer aussi sur",delete:"Supprimer",cancel:"Annuler",apply:"Appliquer",quota_title:"Quota du {day}",minus15:"Retirer 15 minutes",plus15:"Ajouter 15 minutes",no_tv:"Pas de t\xE9l\xE9",preset_none:"Aucun",apply_to:"Appliquer \xE0",copy_title:"Copier le {day}",copy_note:"Quota ({quota}) et plages ({slots}) remplaceront ceux des jours choisis.",to:"Vers",copy:"Copier",add_weekdays:"+ semaine",add_weekend:"+ week-end",add_all:"+ tous",clear:"effacer",dlg_slot:"Modifier la plage",dlg_quota:"Modifier le quota",dlg_copy:"Copier le jour"},info:{merged:"Plages fusionn\xE9es",slot_added:"Plage ajout\xE9e le {day}",slot_deleted:"Plage supprim\xE9e",duplicated:({n:r,merged:e})=>`Plage dupliqu\xE9e sur ${r} ${E(r,"jour","jours")}${e?" (avec fusion)":""}`,quota_applied:({value:r,n:e})=>`Quota de ${r} appliqu\xE9 \xE0 ${e} jours`,day_copied:({Day:r,n:e})=>`${r} copi\xE9 vers ${e} ${E(e,"jour","jours")}`},panel:{views:"Vues",view_children:"Enfants",view_history:"Historique",view_settings:"R\xE9glages",edit_child:"Modifier",delete_child:"Supprimer",discard_confirm:"Des modifications ne sont pas enregistr\xE9es. Les abandonner ?",title:"Plages et quotas",intro:"Quand chaque enfant peut allumer la t\xE9l\xE9 avec son code, et combien de temps par jour.",add_child:"+ Ajouter un enfant",unsaved:"Modifications non enregistr\xE9es",weekly:({total:r,n:e})=>`${r} de t\xE9l\xE9 possible par semaine, sur ${e} ${E(e,"jour","jours")}`,no_day:"Aucun jour autoris\xE9",enabled:"Actif",change_code:"Changer le code",copy_from:"Copier les r\xE8gles de\u2026",undo:"Annuler la derni\xE8re action",checks:"\xC0 v\xE9rifier",all_good:"R\xE8gles coh\xE9rentes pour {name}.",savebar:"Modifications non enregistr\xE9es : {names}",discard:"Abandonner",save:"Enregistrer",saving:"Enregistrement\u2026",saved:"Enregistr\xE9 : {names}",discarded:"Modifications abandonn\xE9es",undone:"Derni\xE8re action annul\xE9e",copied_from:"R\xE8gles de {src} copi\xE9es sur {name}",code_title:"Nouveau code de {name}",code_note:"4 \xE0 8 chiffres. Les codes trop simples (1234, 0000\u2026) sont refus\xE9s.",code:"Code",confirm:"Confirmation",validate:"Valider",code_changed:"Code de {name} modifi\xE9.",no_instance_title:"Aucune t\xE9l\xE9vision configur\xE9e",no_instance_text:"Ajoutez l'int\xE9gration Zapette pour commencer.",open_integrations:"Ouvrir les int\xE9grations",no_child:"Aucun enfant n'est encore d\xE9clar\xE9 pour {tv}.",invalid_child:"Le param\xE9trage de {name} est illisible. Reconfigurez cet enfant depuis la page de l'int\xE9gration, ou supprimez-le.",load_error:"Impossible de charger Zapette : {message}",save_error:"{name} non enregistr\xE9 : {message}",tv:"T\xE9l\xE9vision"},warn:{disabled:"{name} est d\xE9sactiv\xE9 : son code sera refus\xE9.",never:"{name} ne peut jamais regarder la t\xE9l\xE9.",no_slot:"Pas de t\xE9l\xE9 le {day} : aucune plage d\xE9finie.",no_quota:"Pas de t\xE9l\xE9 le {day} : quota \xE0 0.",exceeds:"Le {day}, le quota ({quota}) d\xE9passe la dur\xE9e des plages ({slots})."},error:{value_range:"Valeur hors limites.",value_invalid:"Valeur invalide.",unknown_section:"Section inconnue, rechargez la page.",name_invalid:"Le nom doit comporter 1 \xE0 30 caract\xE8res (lettres, chiffres, espaces, - et ').",already_configured:"Un enfant porte d\xE9j\xE0 ce pr\xE9nom.",tv_name_in_use:"Une autre t\xE9l\xE9vision Zapette porte d\xE9j\xE0 ce nom.",parent_name_in_use:"Un parent porte d\xE9j\xE0 ce nom.",last_parent_code:"Impossible de supprimer le dernier code parent.",plug_not_found:"Choisissez un interrupteur existant.",power_not_found:"Choisissez un capteur de puissance existant.",plug_in_use:"Cette prise est d\xE9j\xE0 utilis\xE9e par une autre t\xE9l\xE9vision Zapette.",keypad_topic_invalid:"Sujet invalide : indiquez zigbee2mqtt/NOM_DU_CLAVIER (sans +, # ni /set).",keypad_in_use:"Ce clavier est d\xE9j\xE0 utilis\xE9 par une autre t\xE9l\xE9vision Zapette.",test_in_progress:"Un test de ce clavier est d\xE9j\xE0 en cours.",unauthorized:"R\xE9serv\xE9 aux administrateurs.",max_slots:"4 plages maximum par jour ({day}).",slot_missing:"Indiquez le d\xE9but et la fin de la plage.",slot_order:"La fin doit \xEAtre apr\xE8s le d\xE9but (00:00 = minuit).",slot_too_short:"Une plage doit durer au moins 5 minutes.",slot_overlap:"Des plages se chevauchent.",slot_too_many:"4 plages maximum par jour.",quota_range:"Le quota doit \xEAtre compris entre 0 et 24 heures.",quota_step:"Le quota doit \xEAtre un multiple de 5 minutes.",code_not_digits:"Le code ne doit contenir que des chiffres.",code_length:"Le code doit comporter entre 4 et 8 chiffres.",code_mismatch:"Les deux codes ne sont pas identiques.",code_too_simple:"Code trop simple (chiffres identiques ou suite). Choisissez-en un autre.",code_in_use:"Ce code est d\xE9j\xE0 utilis\xE9. Choisissez-en un autre.",invalid_data:"Donn\xE9es invalides.",not_found:"\xC9l\xE9ment introuvable, rechargez la page."},history:{title:"Historique",intro:"Qui a regard\xE9 la t\xE9l\xE9, quand, et ce qui s'est pass\xE9. Conserv\xE9 90 jours.",loading:"Chargement de l'historique\u2026",load_error:"Impossible de charger l'historique : {message}",retry:"R\xE9essayer",prev:"Semaine pr\xE9c\xE9dente",next:"Semaine suivante",this_week:"Cette semaine",days:"Jours de la semaine",legend:"L\xE9gende",empty:"Rien \xE0 afficher pour cette semaine.",retention:"L'historique est conserv\xE9 90 jours : cette semaine est trop ancienne.",parents:"Parents",parent:"parent",deleted_child:"{name} (enfant supprim\xE9)",powered:"T\xE9l\xE9 allum\xE9e hors session",powered_short:"Hors session",ongoing:"en cours",interrupted:"Interrompue par un arr\xEAt de Home Assistant",unclean:"D\xE9but estim\xE9 (coupure de courant)",ended_by:"Fin : {reason}",ignore_rules:"R\xE8gles ignor\xE9es",group:"{n} fois, de {first} \xE0 {last}",until:"Jusqu'\xE0 {time}",tolerated:"Allumage manuel tol\xE9r\xE9",recut:"Prise recoup\xE9e",cut:"Prise coup\xE9e",not_cut:"Prise non coup\xE9e (r\xE9glage de d\xE9veloppement)",power_unknown:"Puissance inconnue",seconds:"{n} s",minutes:"{n} min",total_under_minute:"< 1 min",totals:"Temps de t\xE9l\xE9, {day}",total_label:"{name} : {duration} de t\xE9l\xE9 {day}",week_total:"{duration} cette semaine",aria_session:"{name}, de {start} \xE0 {end}",aria_powered:"T\xE9l\xE9 allum\xE9e hors session, de {start} \xE0 {end}",aria_group:"{type}, {n} fois \xE0 partir de {time}",source:{keypad:"Au clavier",action:"Par une action"},origin:{parent:"Allum\xE9e par un parent (bouton ou action)",tolerated:"Allumage manuel tol\xE9r\xE9",control_inactive:"Contr\xF4le suspendu",other:"Allum\xE9e hors de Zapette"},type:{denied:"Acc\xE8s refus\xE9",lockout:"Clavier verrouill\xE9",bypass:"Contournement",standby:"T\xE9l\xE9 en veille",plug_lost:"Prise injoignable",keypad_offline:"Clavier injoignable",control_off:"Contr\xF4le suspendu",ha_down:"Home Assistant arr\xEAt\xE9"},denied:{outside_schedule:"Hors des plages horaires",invalid_code:"Code inconnu",quota_exhausted:"Quota \xE9puis\xE9",profile_blocked:"Enfant d\xE9sactiv\xE9",locked_out:"Clavier verrouill\xE9",plug_unavailable:"Prise injoignable",control_inactive:"Contr\xF4le suspendu",error:"Erreur interne"},end:{user:"code ressaisi",parent:"code parent",keypad_off:"touche d'arr\xEAt",stopped:"arr\xEAt\xE9e par un parent",quota:"quota \xE9puis\xE9",schedule:"fin de la plage horaire",midnight:"minuit",safety_limit:"dur\xE9e maximale atteinte",standby:"t\xE9l\xE9 en veille",plug_off:"prise coup\xE9e",plug_lost:"prise injoignable",control_inactive:"contr\xF4le suspendu",profile_blocked:"enfant d\xE9sactiv\xE9",profile_removed:"enfant supprim\xE9",restart:"red\xE9marrage de Home Assistant",handover:"t\xE9l\xE9 reprise par un autre enfant"}},settings:{title:"R\xE9glages",intro:"Tout ce qui se r\xE8gle pour cette t\xE9l\xE9vision. Chaque section s'enregistre s\xE9par\xE9ment ; la t\xE9l\xE9 n'est ni allum\xE9e ni coup\xE9e par un r\xE9glage.",save:"Enregistrer",cancel:"Annuler",saving:"Enregistrement\u2026",saved:"R\xE9glages enregistr\xE9s : {section}",range:"Entre {min} et {max}.",integer:"Nombre entier attendu.",load_error:"Impossible de charger les r\xE9glages : {message}",status:"\xC9tat et maintenance",status_unavailable:"\xC9tat indisponible (instance non charg\xE9e).",control:"Contr\xF4le actif",control_help:"Suspendu, Zapette ne commande plus la prise : la t\xE9l\xE9 est en acc\xE8s libre.",plug:"Prise",plug_none:"Aucune prise",reachable:"Joignable",unreachable:"Injoignable",problem:"Probl\xE8me signal\xE9",last_outage:"Derni\xE8re perte : {when}",no_outage:"Aucune perte enregistr\xE9e",outages_24h:({n:r})=>`${r} ${E(r,"perte","pertes")} sur 24 h`,keypad:"Clavier",keypad_none:"Aucun clavier",available:"Disponible",unavailable:"Injoignable",battery:"Pile : {level} %",battery_low:"Pile faible : {level} %",locked:"Verrouill\xE9 jusqu'\xE0 {until}",not_locked:"Non verrouill\xE9",unblock:"D\xE9verrouiller le clavier",unblocked:"Clavier d\xE9verrouill\xE9",open_device:"Ouvrir l'appareil dans Home Assistant",unknown:"\u2014",s_identity:"T\xE9l\xE9vision",s_parents:"Codes parents",s_plug:"Prise",s_plug_behavior:"Comportement de la prise",s_keypad:"Clavier",s_keypad_guard:"Anti\u2011essais et touche d'arr\xEAt",s_sessions:"Sessions",tv_name:"Nom de la t\xE9l\xE9vision",tv_name_help:"Renomme aussi l'appareil \xAB Zapette \u2013 \u2026 \xBB ; les identifiants des entit\xE9s ne changent pas.",plug_entity:"Prise de la t\xE9l\xE9",power_entity:"Capteur de puissance (facultatif)",power_none:"Aucun capteur",plug_note:"Changer de prise ne l'allume ni ne la coupe.",missing:"{entity} (introuvable)",parents_help:"Un code parent ouvre une session sans quota ni plage horaire. Les codes ne sont jamais affich\xE9s.",add_parent:"Ajouter un parent",edit_parent:"Modifier",delete_parent:"Supprimer",last_parent:"Il faut au moins un code parent.",parent_title_add:"Nouveau parent",parent_title_edit:"Modifier {name}",parent_name:"Nom",keep_code:"Laisser vide pour garder le code actuel.",parent_added:"Parent ajout\xE9 : {name}",parent_updated:"Parent modifi\xE9 : {name}",parent_deleted:"Parent supprim\xE9 : {name}",delete_parent_title:"Supprimer {name} ?",delete_parent_text:"Son code ne fonctionnera plus.",delete:"Supprimer",keypad_choice:"Clavier Zigbee2MQTT",keypad_manual:"Autre sujet\u2026",keypad_topic:"Sujet MQTT",keypad_found:"{n} clavier(s) trouv\xE9(s)",keypad_search:"Rechercher les claviers",keypad_searching:"Recherche\u2026",keypad_no_mqtt:"MQTT indisponible : saisissez le sujet \xE0 la main.",keypad_test:"Tester le clavier",keypad_test_wait:"Tapez un code puis validez sur le clavier ({topic})\u2026",keypad_test_key:"Touche re\xE7ue : {key}. Le code n'est ni affich\xE9 ni \xE9valu\xE9.",keypad_test_timeout:"Rien re\xE7u en {seconds} s.",keypad_test_no_mqtt:"MQTT indisponible : impossible de tester.",keypad_test_retry:"Recommencer",dev:"R\xE9glage de d\xE9veloppement",f:{tolerate_manual:"Tol\xE9rer l'allumage manuel",standby_threshold:"Seuil de veille",standby_delay:"D\xE9lai de veille",standby_cut:"Couper la prise en veille",lockout_failures:"Codes faux avant verrouillage",lockout_window:"Sur une dur\xE9e de",lockout_duration:"Dur\xE9e du verrouillage",off_key:"Touche d'arr\xEAt (seule, sans code)",warning_minutes:"Avertissement avant coupure",warning_beep:"Bip du clavier",parent_max_hours:"Dur\xE9e maximale d'une session parent"},h:{tolerate_manual:"Une prise allum\xE9e par son bouton ou une autre automatisation n'est pas recoup\xE9e (l'\xE9v\xE9nement est quand m\xEAme envoy\xE9).",standby_threshold:"Sous cette puissance, la t\xE9l\xE9 est consid\xE9r\xE9e \xE9teinte \xE0 la t\xE9l\xE9commande.",standby_delay:"Temps sous le seuil avant que la veille termine la session.",standby_cut:"Activ\xE9 (recommand\xE9) : la veille termine la session et coupe la prise. D\xE9sactiv\xE9 : la veille est seulement signal\xE9e \u2014 pour les essais sans t\xE9l\xE9 branch\xE9e.",off_key:"Sur le frient KEPZB\u2011110, le cadenas est \xAB Armer toutes les zones \xBB.",warning_minutes:"0 = aucun avertissement.",warning_beep:"Si le clavier le permet, il bipe quelques secondes \xE0 l'avertissement.",parent_max_hours:"0 = jamais."},off_key:{none:"Aucune",arm_all_zones:"Armer toutes les zones (cadenas)",arm_day_zones:"Armer zones de jour",arm_night_zones:"Armer zones de nuit",disarm:"D\xE9sarmer"}},child:{add_title:"Nouvel enfant",edit_title:"Modifier {name}",name:"Pr\xE9nom",icon:"Ic\xF4ne",icon_help:"Nom d'ic\xF4ne Material Design, par exemple mdi:face-woman.",template:"R\xE8gles de d\xE9part",template_default:"R\xE8gles par d\xE9faut",template_empty:"Aucune t\xE9l\xE9 (\xE0 r\xE9gler ensuite)",template_copy:"Copier les r\xE8gles de {name}",create:"Ajouter",save:"Enregistrer",created:"{name} ajout\xE9.",renamed:"{name} enregistr\xE9.",deleted:"{name} supprim\xE9.",delete_title:"Supprimer {name} ?",delete_text:"Son code, ses r\xE8gles et ses entit\xE9s seront supprim\xE9s. Son historique est conserv\xE9 90 jours.",delete_session:"{name} regarde la t\xE9l\xE9 : sa session sera termin\xE9e.",delete:"Supprimer"}},xt={days:[["Mon","Monday"],["Tue","Tuesday"],["Wed","Wednesday"],["Thu","Thursday"],["Fri","Friday"],["Sat","Saturday"],["Sun","Sunday"]],grid:{hint_mouse:"Drag in a column to create a time slot, stretch its edges to adjust it, move it to another day.",hint_touch:"Tap a column to create a 1-hour slot, then tap the slot to adjust it.",fine:"5-min steps",night:"Show night",copy_day_aria:"Copy {day} to other days",quota_aria:"{Day} quota: {value}. Edit.",none_m:"none",none_f:"none",gauge_title:"Quota {quota} out of {total} of time slots",gauge_none:"No time slot",slot_aria:"{Day}, from {start} to {end}. Enter to edit, arrows to move, Delete to remove.",now:"Now",slot_title:"{Day} time slot",start:"Start",end:"End",slot_note:"5-minute precision. End at 00:00 = midnight.",duplicate_on:"Also duplicate on",delete:"Delete",cancel:"Cancel",apply:"Apply",quota_title:"{Day} quota",minus15:"Remove 15 minutes",plus15:"Add 15 minutes",no_tv:"No TV",preset_none:"None",apply_to:"Apply to",copy_title:"Copy {Day}",copy_note:"Quota ({quota}) and time slots ({slots}) will replace those of the selected days.",to:"To",copy:"Copy",add_weekdays:"+ weekdays",add_weekend:"+ weekend",add_all:"+ all",clear:"clear",dlg_slot:"Edit time slot",dlg_quota:"Edit quota",dlg_copy:"Copy day"},info:{merged:"Time slots merged",slot_added:"Time slot added on {Day}",slot_deleted:"Time slot deleted",duplicated:({n:r,merged:e})=>`Time slot duplicated on ${r} ${E(r,"day","days")}${e?" (merged)":""}`,quota_applied:({value:r,n:e})=>`${r} quota applied to ${e} days`,day_copied:({Day:r,n:e})=>`${r} copied to ${e} ${E(e,"day","days")}`},panel:{views:"Views",view_children:"Children",view_history:"History",view_settings:"Settings",edit_child:"Edit",delete_child:"Delete",discard_confirm:"Some changes are not saved. Discard them?",title:"Time slots and quotas",intro:"When each child can turn the TV on with their code, and for how long each day.",add_child:"+ Add a child",unsaved:"Unsaved changes",weekly:({total:r,n:e})=>`Up to ${r} of TV per week, over ${e} ${E(e,"day","days")}`,no_day:"No allowed day",enabled:"Enabled",change_code:"Change code",copy_from:"Copy rules from\u2026",undo:"Undo last action",checks:"To check",all_good:"Rules are consistent for {name}.",savebar:"Unsaved changes: {names}",discard:"Discard",save:"Save",saving:"Saving\u2026",saved:"Saved: {names}",discarded:"Changes discarded",undone:"Last action undone",copied_from:"Rules copied from {src} to {name}",code_title:"New code for {name}",code_note:"4 to 8 digits. Codes that are too simple (1234, 0000\u2026) are refused.",code:"Code",confirm:"Confirm",validate:"Confirm",code_changed:"{name}'s code changed.",no_instance_title:"No TV configured",no_instance_text:"Add the Zapette integration to get started.",open_integrations:"Open integrations",no_child:"No child declared yet for {tv}.",invalid_child:"{name}'s settings cannot be read. Reconfigure this child from the integration page, or delete it.",load_error:"Cannot load Zapette: {message}",save_error:"{name} not saved: {message}",tv:"TV"},warn:{disabled:"{name} is disabled: their code will be refused.",never:"{name} can never watch TV.",no_slot:"No TV on {Day}: no time slot.",no_quota:"No TV on {Day}: quota is 0.",exceeds:"On {Day}, the quota ({quota}) exceeds the time slots ({slots})."},error:{value_range:"Value out of range.",value_invalid:"Invalid value.",unknown_section:"Unknown section, reload the page.",name_invalid:"The name must have 1 to 30 characters (letters, digits, spaces, - and ').",already_configured:"A child already has this name.",tv_name_in_use:"Another Zapette TV already has this name.",parent_name_in_use:"A parent already has this name.",last_parent_code:"The last parent code cannot be deleted.",plug_not_found:"Choose an existing switch.",power_not_found:"Choose an existing power sensor.",plug_in_use:"This plug is already used by another Zapette TV.",keypad_topic_invalid:"Invalid topic: enter zigbee2mqtt/KEYPAD_NAME (no +, # or /set).",keypad_in_use:"This keypad is already used by another Zapette TV.",test_in_progress:"A test of this keypad is already running.",unauthorized:"Administrators only.",max_slots:"4 time slots maximum per day ({Day}).",slot_missing:"Enter both start and end of the time slot.",slot_order:"The end must be after the start (00:00 = midnight).",slot_too_short:"A time slot must last at least 5 minutes.",slot_overlap:"Time slots overlap.",slot_too_many:"4 time slots maximum per day.",quota_range:"The quota must be between 0 and 24 hours.",quota_step:"The quota must be a multiple of 5 minutes.",code_not_digits:"The code must contain digits only.",code_length:"The code must have 4 to 8 digits.",code_mismatch:"The two codes do not match.",code_too_simple:"Code too simple (repeated digits or sequence). Choose another one.",code_in_use:"This code is already in use. Choose another one.",invalid_data:"Invalid data.",not_found:"Item not found, reload the page."},history:{title:"History",intro:"Who watched TV, when, and what happened. Kept for 90 days.",loading:"Loading history\u2026",load_error:"Unable to load history: {message}",retry:"Retry",prev:"Previous week",next:"Next week",this_week:"This week",days:"Days of the week",legend:"Legend",empty:"Nothing to show for this week.",retention:"History is kept for 90 days: this week is too old.",parents:"Parents",parent:"parent",deleted_child:"{name} (deleted child)",powered:"TV on outside a session",powered_short:"No session",ongoing:"ongoing",interrupted:"Interrupted by a Home Assistant shutdown",unclean:"Estimated start (power cut)",ended_by:"Ended: {reason}",ignore_rules:"Rules ignored",group:"{n} times, from {first} to {last}",until:"Until {time}",tolerated:"Manual turn-on tolerated",recut:"Plug turned off again",cut:"Plug turned off",not_cut:"Plug left on (development setting)",power_unknown:"Unknown power",seconds:"{n} s",minutes:"{n} min",total_under_minute:"< 1 min",totals:"TV time, {day}",total_label:"{name}: {duration} of TV on {day}",week_total:"{duration} this week",aria_session:"{name}, from {start} to {end}",aria_powered:"TV on outside a session, from {start} to {end}",aria_group:"{type}, {n} times from {time}",source:{keypad:"From the keypad",action:"From an action"},origin:{parent:"Turned on by a parent (button or action)",tolerated:"Manual turn-on tolerated",control_inactive:"Control suspended",other:"Turned on outside Zapette"},type:{denied:"Access denied",lockout:"Keypad locked",bypass:"Bypass",standby:"TV on standby",plug_lost:"Plug unreachable",keypad_offline:"Keypad unreachable",control_off:"Control suspended",ha_down:"Home Assistant stopped"},denied:{outside_schedule:"Outside the time slots",invalid_code:"Unknown code",quota_exhausted:"Quota used up",profile_blocked:"Child disabled",locked_out:"Keypad locked",plug_unavailable:"Plug unreachable",control_inactive:"Control suspended",error:"Internal error"},end:{user:"code entered again",parent:"parent code",keypad_off:"stop key",stopped:"stopped by a parent",quota:"quota used up",schedule:"end of the time slot",midnight:"midnight",safety_limit:"maximum duration reached",standby:"TV on standby",plug_off:"plug turned off",plug_lost:"plug unreachable",control_inactive:"control suspended",profile_blocked:"child disabled",profile_removed:"child deleted",restart:"Home Assistant restart",handover:"TV taken over by another child"}},settings:{title:"Settings",intro:"Everything that can be set for this TV. Each section is saved on its own; a setting never turns the TV on or off.",save:"Save",cancel:"Cancel",saving:"Saving\u2026",saved:"Settings saved: {section}",range:"Between {min} and {max}.",integer:"Whole number expected.",load_error:"Cannot load the settings: {message}",status:"Status and maintenance",status_unavailable:"Status unavailable (instance not loaded).",control:"Control active",control_help:"When suspended, Zapette no longer drives the plug: the TV is freely available.",plug:"Plug",plug_none:"No plug",reachable:"Reachable",unreachable:"Unreachable",problem:"Problem reported",last_outage:"Last outage: {when}",no_outage:"No outage recorded",outages_24h:({n:r})=>`${r} ${E(r,"outage","outages")} in 24 h`,keypad:"Keypad",keypad_none:"No keypad",available:"Available",unavailable:"Unreachable",battery:"Battery: {level} %",battery_low:"Battery low: {level} %",locked:"Locked until {until}",not_locked:"Not locked",unblock:"Unlock the keypad",unblocked:"Keypad unlocked",open_device:"Open the device in Home Assistant",unknown:"\u2014",s_identity:"TV",s_parents:"Parent codes",s_plug:"Plug",s_plug_behavior:"Plug behaviour",s_keypad:"Keypad",s_keypad_guard:"Wrong code protection and stop key",s_sessions:"Sessions",tv_name:"TV name",tv_name_help:"Also renames the \u201CZapette \u2013 \u2026\u201D device; entity IDs do not change.",plug_entity:"TV plug",power_entity:"Power sensor (optional)",power_none:"No sensor",plug_note:"Changing the plug neither turns it on nor off.",missing:"{entity} (not found)",parents_help:"A parent code opens a session without quota or time slots. Codes are never shown.",add_parent:"Add a parent",edit_parent:"Edit",delete_parent:"Delete",last_parent:"At least one parent code is required.",parent_title_add:"New parent",parent_title_edit:"Edit {name}",parent_name:"Name",keep_code:"Leave empty to keep the current code.",parent_added:"Parent added: {name}",parent_updated:"Parent updated: {name}",parent_deleted:"Parent deleted: {name}",delete_parent_title:"Delete {name}?",delete_parent_text:"Their code will no longer work.",delete:"Delete",keypad_choice:"Zigbee2MQTT keypad",keypad_manual:"Other topic\u2026",keypad_topic:"MQTT topic",keypad_found:"{n} keypad(s) found",keypad_search:"Search keypads",keypad_searching:"Searching\u2026",keypad_no_mqtt:"MQTT unavailable: enter the topic manually.",keypad_test:"Test the keypad",keypad_test_wait:"Type a code and confirm it on the keypad ({topic})\u2026",keypad_test_key:"Key received: {key}. The code is neither shown nor checked.",keypad_test_timeout:"Nothing received in {seconds} s.",keypad_test_no_mqtt:"MQTT unavailable: cannot test.",keypad_test_retry:"Try again",dev:"Development setting",f:{tolerate_manual:"Tolerate turning on manually",standby_threshold:"Standby threshold",standby_delay:"Standby delay",standby_cut:"Turn the plug off on standby",lockout_failures:"Wrong codes before lockout",lockout_window:"Within",lockout_duration:"Lockout duration",off_key:"Stop key (alone, without code)",warning_minutes:"Warning before cut-off",warning_beep:"Keypad beep",parent_max_hours:"Maximum length of a parent session"},h:{tolerate_manual:"A plug turned on with its button or by another automation is not turned off again (the event is still sent).",standby_threshold:"Below this power, the TV is considered off with the remote.",standby_delay:"Time below the threshold before standby ends the session.",standby_cut:"On (recommended): standby ends the session and turns the plug off. Off: standby is only reported \u2014 for tests without a TV plugged in.",off_key:"On the frient KEPZB-110, the padlock key is \u201CArm all zones\u201D.",warning_minutes:"0 = no warning.",warning_beep:"If the keypad allows it, it beeps for a few seconds when the warning is given.",parent_max_hours:"0 = never."},off_key:{none:"None",arm_all_zones:"Arm all zones (padlock)",arm_day_zones:"Arm day zones",arm_night_zones:"Arm night zones",disarm:"Disarm"}},child:{add_title:"New child",edit_title:"Edit {name}",name:"First name",icon:"Icon",icon_help:"Material Design icon name, for example mdi:face-woman.",template:"Starting rules",template_default:"Default rules",template_empty:"No TV (to be set afterwards)",template_copy:"Copy {name}'s rules",create:"Add",save:"Save",created:"{name} added.",renamed:"{name} saved.",deleted:"{name} deleted.",delete_title:"Delete {name}?",delete_text:"Their code, rules and entities will be deleted. Their history is kept for 90 days.",delete_session:"{name} is watching TV: the session will end.",delete:"Delete"}},$t=r=>r&&r[0].toUpperCase()+r.slice(1);function Fe(r){let e=String(r||"en").startsWith("fr")?Ye:xt,t=(s,a={})=>{let i={...a};typeof i.day=="number"&&(i.Day=$t(e.days[i.day][1]),i.day=e.days[i.day][1]);let n=s.split(".").reduce((l,d)=>l?.[d],e);return n==null?s:typeof n=="function"?n(i):n.replace(/\{(\w+)\}/g,(l,d)=>i[d]??"")};return t.days=e.days,t.dur=b,t.lang=e===Ye?"fr":"en",t}var fe="mdi:account-child",ye=class extends y{static properties={hass:{attribute:!1},entryId:{attribute:!1},t:{attribute:!1},kids:{attribute:!1},_mode:{state:!0},_kid:{state:!0},_error:{state:!0},_busy:{state:!0},_icon:{state:!0}};constructor(){super(),this._mode=null,this._kid=null,this._icon=fe}openAdd(){this._open("add",null)}openEdit(e){this._open("edit",e)}openDelete(e){this._open("delete",e)}async _open(e,t){this._mode=e,this._kid=t,this._error=null,this._icon=t?.icon??fe,await this.updateComplete;let s=this.renderRoot.querySelector("dialog"),a=s.querySelector("form").elements;for(let[i,n]of[["cname",t?.name??""],["icon",this._icon],["code",""],["confirm",""],["template","default"]])a.namedItem(i)&&(a.namedItem(i).value=n);s.showModal()}_close(){this.renderRoot.querySelector("dialog")?.close()}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:t,bubbles:!0,composed:!0}))}_errorText(e){let t=this.t(`error.${e.code}`);return t===`error.${e.code}`?e.message??String(e):t}async _submit(e){e.preventDefault();let t=this.t,s=e.target.elements,a=this._kid,i={entry_id:this.entryId},n;if(this._mode==="delete")n={...i,type:"zapette/child/delete",subentry_id:a.subentry_id};else if(this._mode==="edit")n={...i,type:"zapette/child/rename",subentry_id:a.subentry_id,name:s.namedItem("cname").value,icon:s.namedItem("icon").value.trim()||null};else{let l=s.namedItem("code"),d=s.namedItem("confirm");n={...i,type:"zapette/child/create",name:s.namedItem("cname").value,icon:s.namedItem("icon").value.trim()||null,code:l.value,code_confirm:d.value,template:s.namedItem("template").value},l.value="",d.value=""}this._busy=!0;try{let l=await this.hass.callWS(n),d={add:"created",edit:"renamed",delete:"deleted"}[this._mode],c=l?.name??a.name;this._close(),this._emit("child-changed",{action:d,subentry_id:l?.subentry_id??a.subentry_id}),this._emit("toast",{text:t(`child.${d}`,{name:c}),kind:"ok"})}catch(l){this._error=this._errorText(l)}finally{this._busy=!1}}_renderFields(){let e=this.t,t=this._mode==="add",s=(this.kids??[]).filter(i=>!i.invalid),a=customElements.get("ha-icon")&&/^[a-z]+:[a-z0-9-]+$/.test(this._icon);return o`
      <label for="c-name">${e("child.name")}
        <input id="c-name" name="cname" type="text" maxlength="30" autocomplete="off" required>
      </label>
      <label for="c-icon">${e("child.icon")}
        <span class="iconrow">
          <input id="c-icon" name="icon" type="text" autocomplete="off" spellcheck="false" placeholder=${fe}
                 @input=${i=>this._icon=i.target.value.trim()}>
          ${a?o`<ha-icon .icon=${this._icon}></ha-icon>`:p}
        </span>
        <span class="hint">${e("child.icon_help")}</span>
      </label>
      ${t?o`
        <label for="c-code">${e("panel.code")}
          <input id="c-code" name="code" type="password" inputmode="numeric" autocomplete="off" required>
        </label>
        <label for="c-confirm">${e("panel.confirm")}
          <input id="c-confirm" name="confirm" type="password" inputmode="numeric" autocomplete="off" required>
        </label>
        <p class="note">${e("panel.code_note")}</p>
        <label for="c-template">${e("child.template")}
          <select id="c-template" name="template">
            <option value="default">${e("child.template_default")}</option>
            <option value="empty">${e("child.template_empty")}</option>
            ${s.map(i=>o`<option value=${`copy:${i.subentry_id}`}>${e("child.template_copy",{name:i.name})}</option>`)}
          </select>
        </label>`:p}`}render(){let e=this.t;if(!e)return p;let t=this._kid,s=this._mode,a=s==="add"?e("child.add_title"):s==="edit"?e("child.edit_title",{name:t?.name}):s==="delete"?e("child.delete_title",{name:t?.name}):"";return o`
      <dialog aria-labelledby="child-title" @close=${()=>this._mode=null}>
        <form @submit=${this._submit} novalidate>
          <h2 id="child-title">${a}</h2>
          ${s==="delete"?o`
            <p class="note">${e("child.delete_text")}</p>
            ${t?.in_session?o`<p class="warn" role="alert">${e("child.delete_session",{name:t.name})}</p>`:p}`:s?this._renderFields():p}
          ${this._error?o`<p class="error" role="alert">${this._error}</p>`:p}
          <div class="actions">
            <span class="grow"></span>
            <button type="button" class="text" @click=${this._close}>${e("settings.cancel")}</button>
            <button type="submit" class="filled ${s==="delete"?"danger":""}" ?disabled=${this._busy}>
              ${e(s==="delete"?"child.delete":s==="add"?"child.create":"child.save")}</button>
          </div>
        </form>
      </dialog>`}static styles=$`
    dialog {
      border: 1px solid var(--zp-line); border-radius: 18px; padding: 22px; background: var(--zp-raised); color: var(--zp-ink);
      width: min(92vw, 420px); box-sizing: border-box; box-shadow: var(--zp-shadow);
    }
    dialog::backdrop { background: rgb(0 0 0 / .4); }
    form { display: grid; gap: 12px; }
    h2 { margin: 0; font-size: 18px; font-weight: 500; }
    label { display: grid; gap: 4px; font-size: 12.5px; color: var(--zp-muted); }
    input, select {
      font: inherit; font-size: 16px; color: var(--zp-ink); border: 1px solid var(--zp-line); border-radius: 8px; padding: 9px 10px;
      background: var(--zp-card); min-width: 0; width: 100%; box-sizing: border-box;
    }
    input[type="password"] { letter-spacing: .2em; }
    .iconrow { display: flex; gap: 8px; align-items: center; }
    .iconrow ha-icon { flex: none; color: var(--zp-ink); }
    .hint, .note { color: var(--zp-muted); font-size: 12.5px; line-height: 1.4; margin: 0; }
    .warn { margin: 0; padding: 10px 12px; border-radius: 10px; background: var(--zp-warn-bg); color: var(--zp-ink); }
    .error { margin: 0; color: var(--zp-danger); font-size: 13px; }
    .actions { display: flex; gap: 6px; align-items: center; }
    .grow { flex: 1; }
    button { font: inherit; border: 0; border-radius: 999px; padding: 8px 16px; cursor: pointer; font-weight: 500; }
    .text { background: none; color: var(--zp-primary); }
    .filled { background: var(--zp-primary); color: var(--zp-primary-ink); }
    .filled.danger { background: var(--zp-danger); color: #fff; }
    button:disabled { opacity: .5; cursor: default; }
    button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 2px; }
    @media (max-width: 599px) {
      dialog { width: 100vw; max-width: 100vw; height: 100dvh; max-height: 100dvh; margin: 0; border-radius: 0; }
    }
  `};customElements.define("zapette-child-dialogs",ye);var wt={denied:w`<circle cx="12" cy="12" r="8"/><path d="M6.5 6.5l11 11"/>`,lockout:w`<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>`,bypass:w`<path d="M13 3 6 13h5l-1 8 7-10h-5l1-8z"/>`,standby:w`<path d="M19.5 14.5A8 8 0 1 1 9.5 4.5a6.5 6.5 0 0 0 10 10z"/>`,plug_lost:w`<path d="M9 3v4M15 3v4M6 7h12v4a6 6 0 0 1-12 0V7zM12 17v4"/><path d="M4 4l16 16"/>`,keypad_offline:w`<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9.5 8h.01M14.5 8h.01M9.5 12h.01M14.5 12h.01M9.5 16h.01M14.5 16h.01"/><path d="M3 4l18 16"/>`,control_off:w`<path d="M9 5v14M15 5v14"/>`,ha_down:w`<path d="M12 3v8"/><path d="M6.3 6.8a8 8 0 1 0 11.4 0"/>`,prev:w`<path d="M15 6l-6 6 6 6"/>`,next:w`<path d="M9 6l6 6-6 6"/>`},Q=r=>o`<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${wt[r]}</svg>`;var kt=6e4,zt=640,Ze=22,At=50,St=["plug_lost","keypad_offline","control_off","ha_down"],Et=["denied","lockout","bypass","standby"],Je=(r,e)=>{let[t,s,a]=r.split("-").map(Number);return new Date(Date.UTC(t,s-1,a+e)).toISOString().slice(0,10)},Xe=r=>{let[e,t,s]=r.split("-").map(Number);return new Date(Date.UTC(e,t-1,s))},be=class extends y{static properties={hass:{attribute:!1},entryId:{attribute:!1},t:{attribute:!1},_data:{state:!0},_error:{state:!0},_loading:{state:!0},_showNight:{state:!0},_day:{state:!0},_pop:{state:!0},_narrow:{state:!0}};constructor(){super(),this._data=null,this._showNight=!1,this._day=null,this._pop=null,this._narrow=!1,this._resize=new ResizeObserver(([e])=>this._narrow=e.contentRect.width<zt),this._onVisible=()=>{document.visibilityState==="visible"&&this._data?.current_week&&this._load(this._data.week_start,!0)},this._onKey=e=>{e.key==="Escape"&&this._pop&&this._closePop()}}connectedCallback(){super.connectedCallback(),this._resize.observe(this),document.addEventListener("visibilitychange",this._onVisible),window.addEventListener("keydown",this._onKey),this._timer=setInterval(()=>{this._data?.current_week&&document.visibilityState==="visible"&&this._load(this._data.week_start,!0)},kt)}disconnectedCallback(){this._resize.disconnect(),document.removeEventListener("visibilitychange",this._onVisible),window.removeEventListener("keydown",this._onKey),clearInterval(this._timer),super.disconnectedCallback()}willUpdate(e){e.has("entryId")&&this.entryId&&this.hass&&(this._data=null,this._day=null,this._load(void 0))}async _load(e,t=!1){let s=this.entryId;t||(this._loading=!0);try{let a=await this.hass.callWS({type:"zapette/history/week",entry_id:s,...e?{week:e}:{}});if(s!==this.entryId)return;let i=a.week_start!==this._data?.week_start;this._data=a,this._error=null,i&&(this._pop=null,this._day=a.current_week?a.days.findIndex(n=>n.date===a.today):0)}catch(a){t||(this._error=a.message??String(a))}finally{this._loading=!1}}_go(e){this._data&&this._load(Je(this._data.week_start,7*e))}get _tz(){return this.hass?.config?.time_zone}_time(e,t=!1){let s={hour:"2-digit",minute:"2-digit",timeZone:this._tz};return t&&Object.assign(s,{weekday:"short",day:"numeric"}),new Intl.DateTimeFormat(this.t.lang,s).format(new Date(e))}_duration(e){let t=this.t;if(e<60)return t("history.seconds",{n:e});let s=Math.round(e/60);if(s<60)return t("history.minutes",{n:s});let a=Math.floor(s/60),i=s%60;return i?`${a} h ${String(i).padStart(2,"0")}`:`${a} h`}_range(){let e=Xe(this._data.week_start),t=Xe(Je(this._data.week_start,6)),s=(a,i)=>new Intl.DateTimeFormat(this.t.lang,{day:"numeric",month:"short",...i?{year:"numeric"}:{},timeZone:"UTC"}).format(a);return`${s(e,!1)} \u2013 ${s(t,!0)}`}_total(e){let t=this.t;if(e<60)return t("history.total_under_minute");let s=Math.floor(e/60);if(s<60)return t("history.minutes",{n:s});let a=Math.floor(s/60),i=s%60;return i?`${a} h ${String(i).padStart(2,"0")}`:`${a} h`}_renderTotals(e,t){if(!e.totals?.length)return p;let s=this.t,a=`${s.days[t][1]} ${Number(e.date.slice(8))}`;return o`
      <ul class="totals" aria-label=${s("history.totals",{day:a})}>
        ${e.totals.map(i=>{let n=this._total(i.seconds),l=s("history.total_label",{name:this._name({...i,kind:"child"}),duration:n,day:a});return o`
            <li class=${i.deleted?"deleted":""} tabindex="0" aria-label=${l} title=${l}
                style="--c:${N(i.color)}">
              <span class="who">${i.name}</span><strong>${n}</strong>
            </li>`})}
      </ul>`}_name(e){let t=this.t;return e.kind==="parent"?e.name?`${e.name} (${t("history.parent")})`:t("history.parents"):e.deleted?t("history.deleted_child",{name:e.name??"?"}):e.name}_openPop(e,t,s,a=!1){if(a&&this._pop&&!this._pop.hover)return;let i=this.getBoundingClientRect(),n=e.currentTarget.getBoundingClientRect(),l=Math.min(Math.max(8,n.right-i.left+6),i.width-296),d=l+290>i.width?Math.max(8,n.left-i.left-296):l;this._pop={item:t,kind:s,hover:a,x:d,y:n.top-i.top}}_closePop(){let e=this._pop?.focus;this._pop=null,e?.focus?.()}_activate(e,t,s){if(this._pop&&!this._pop.hover&&this._pop.item===t){this._closePop();return}this._openPop(e,t,s),this._pop={...this._pop,focus:e.currentTarget}}_popLines(){let e=this.t,{item:t,kind:s}=this._pop;if(s==="session"){let i=t.continued_before||t.continued_after,n=[`${this._time(t.start,i)} \u2192 ${t.end?this._time(t.end,i):e("history.ongoing")} (${this._duration(t.duration)})`];return t.kind==="powered"?(n.push(e(`history.origin.${t.origin??"other"}`)),t.interrupted&&n.push(e("history.interrupted")),{title:e("history.powered"),lines:n}):(t.reason&&n.push(e("history.ended_by",{reason:e(`history.end.${t.reason}`)})),t.source&&n.push(e(`history.source.${t.source}`)),t.ignore_rules&&n.push(e("history.ignore_rules")),{title:this._name(t),lines:n})}if(s==="band"){let i=[`${this._time(t.start,!0)} \u2192 ${t.end?this._time(t.end,!0):e("history.ongoing")} (${this._duration(t.duration)})`];return t.interrupted&&i.push(e("history.interrupted")),t.unclean&&i.push(e("history.unclean")),{title:e(`history.type.${t.type}`),lines:i}}let a=[];return t.count>1?a.push(e("history.group",{n:t.count,first:this._time(t.first),last:this._time(t.last)})):a.push(this._time(t.first)),t.profile_id&&a.push(this._name(t)),t.type==="denied"&&a.push(e(`history.denied.${t.reason}`)),t.type==="lockout"&&a.push(e("history.until",{time:this._time(t.until)})),t.type==="bypass"&&a.push(e(t.tolerated?"history.tolerated":"history.recut")),t.type==="standby"&&(a.push(t.power!=null?`${Math.round(t.power)} W`:e("history.power_unknown")),a.push(e(t.cut?"history.cut":"history.not_cut"))),t.type==="denied"&&t.source&&a.push(e(`history.source.${t.source}`)),{title:e(`history.type.${t.type}`),lines:a}}_renderPop(){let{title:e,lines:t}=this._popLines();return o`
      ${this._pop.hover?p:o`<div class="backdrop" @click=${this._closePop}></div>`}
      <div class="pop ${this._pop.hover?"hover":""}" role="dialog" aria-label=${e}
           style="left:${this._pop.x}px; top:${this._pop.y}px">
        <h3>${e}</h3>
        ${t.map(s=>o`<p>${s}</p>`)}
      </div>`}get _px(){return this._narrow?.62:.8}get _top(){if(this._showNight)return 0;let e=this._data?.earliest;return Math.floor(Math.min(360,e??360)/60)*60}_sessionLabel(e,t){if(t<16)return p;let s=e.kind==="powered"?this.t("history.powered_short"):e.deleted?e.name:e.name??"";return o`<span class="label">${s}${t>=32?o`<small>${m(Math.floor(e.from))}–${e.to>=f?"24:00":m(Math.floor(e.to))}</small>`:p}</span>`}_renderColumn(e,t,s,a){let i=this.t,n=this._data,l=n.current_week&&e.date===n.today,d=u=>(Math.max(u,s)-s)*a,c=[...e.bands.map(u=>({kind:"band",item:u,minute:u.from,type:u.type})),...e.markers.map(u=>({kind:"marker",item:u,minute:u.minute,type:u.type}))].sort((u,g)=>u.minute-g.minute),h=-1/0;for(let u of c)u.top=Math.max(d(u.minute)-Ze/2,h+Ze,0),h=u.top;let _=[...e.sessions].sort((u,g)=>u.from-g.from);return o`
      <div class="col ${l?"today":""}" role="group" aria-label=${i.days[t][1]}>
        ${e.bands.map(u=>o`
          <div class="band ${u.type}" style="top:${d(u.from)}px; height:${Math.max(2,(u.to-Math.max(u.from,s))*a)}px"></div>`)}
        ${_.map(u=>{let g=Math.max(6,(u.to-Math.max(u.from,s))*a),v=u.kind==="powered"?i("history.aria_powered",{start:m(Math.floor(u.from)),end:m(Math.floor(u.to)%f)}):i("history.aria_session",{name:this._name(u),start:m(Math.floor(u.from)),end:m(Math.floor(u.to)%f)});return o`
            <button class="session ${u.kind} ${u.deleted?"deleted":""} ${u.ongoing?"ongoing":""} ${g<16?"thin":""}"
                    style="top:${d(u.from)}px; height:${g}px; --c:${N(u.color)}" aria-label=${v}
                    @click=${z=>this._activate(z,u,"session")}
                    @mouseenter=${z=>this._openPop(z,u,"session",!0)} @mouseleave=${this._leave}>
              ${this._sessionLabel(u,g)}
            </button>`})}
        ${c.map(({kind:u,item:g,type:v,top:z})=>o`
          <button class="mark ${v}" style="top:${z}px" aria-label=${this._markLabel(u,g)}
                  @click=${R=>this._activate(R,g,u)}
                  @mouseenter=${R=>this._openPop(R,g,u,!0)} @mouseleave=${this._leave}>
            ${Q(v)}${u==="marker"&&g.count>1?o`<span class="count">×${g.count}</span>`:p}
          </button>`)}
        ${l&&n.now_minute>=s?o`<div class="now" style="top:${d(n.now_minute)}px" title=${i("grid.now")}></div>`:p}
      </div>`}_leave=()=>{this._pop?.hover&&(this._pop=null)};_markLabel(e,t){let s=this.t,a=s(`history.type.${t.type}`),i=m(Math.floor(e==="band"?t.from:t.minute));return e==="marker"&&t.count>1?s("history.aria_group",{type:a,n:t.count,time:i}):`${a}, ${i}`}_renderLegend(){let e=this.t,t=this._data,s=t.days.flatMap(n=>[...n.bands.map(l=>l.type),...n.markers.map(l=>l.type)]),a=[...St,...Et].filter(n=>s.includes(n)),i=t.days.some(n=>n.sessions.some(l=>l.kind==="powered"));return!t.profiles.length&&!a.length&&!i?p:o`
      <ul class="legend" aria-label=${e("history.legend")}>
        ${t.profiles.map(n=>o`
          <li class=${n.deleted?"deleted":""}><span class="swatch" style="--c:${N(n.color)}"></span>${this._name(n)}${n.week_seconds?o`<span class="week-total">— ${e("history.week_total",{duration:this._total(n.week_seconds)})}</span>`:p}</li>`)}
        ${i?o`<li><span class="swatch powered"></span>${e("history.powered")}</li>`:p}
        ${a.map(n=>o`<li><span class="mark-icon ${n}">${Q(n)}</span>${e(`history.type.${n}`)}</li>`)}
      </ul>`}_renderStrip(){let e=this.t,t=this._data;return o`
      <div class="strip" role="tablist" aria-label=${e("history.days")} @keydown=${this._stripKey}>
        ${t.days.map((s,a)=>{let i=s.sessions.length||s.markers.length||s.bands.length;return o`
            <button role="tab" aria-selected=${a===this._day} tabindex=${a===this._day?0:-1}
                    class=${t.current_week&&s.date===t.today?"today":""}
                    aria-label=${`${e.days[a][1]} ${Number(s.date.slice(8))}`} @click=${()=>this._select(a)}>
              <span>${e.days[a][0]}</span><strong>${Number(s.date.slice(8))}</strong>
              <i class=${i?"dot on":"dot"}></i>
            </button>`})}
      </div>`}_select(e){this._day=Math.max(0,Math.min(6,e)),this._pop=null}_stripKey(e){let t={ArrowLeft:-1,ArrowRight:1}[e.key];t&&(e.preventDefault(),this._select(this._day+t),this.updateComplete.then(()=>this.renderRoot.querySelector(".strip [aria-selected=true]")?.focus()))}_swipeStart(e){this._swipe=e.pointerType==="mouse"?null:{x:e.clientX,y:e.clientY}}_swipeEnd(e){let t=this._swipe;if(this._swipe=null,!t)return;let s=e.clientX-t.x;Math.abs(s)>At&&Math.abs(s)>Math.abs(e.clientY-t.y)&&this._select(this._day+(s<0?1:-1))}render(){if(!this.t)return p;let e=this.t,t=this._data;if(this._error&&!t)return o`<div class="state"><p>${e("history.load_error",{message:this._error})}</p>
        <button class="filled" @click=${()=>this._load(void 0)}>${e("history.retry")}</button></div>`;if(!t)return o`<div class="state loading" aria-busy="true">${e("history.loading")}</div>`;let s=this._px,a=this._top,i=[];for(let c=a;c<=f;c+=60)i.push(c);let n=t.days.every(c=>!c.sessions.length&&!c.markers.length&&!c.bands.length),l=this._narrow,d=l?[this._day??0]:[0,1,2,3,4,5,6];return o`
      <div class="head">
        <div class="nav">
          <button class="round" @click=${()=>this._go(-1)} aria-label=${e("history.prev")} title=${e("history.prev")}>${Q("prev")}</button>
          <h2 aria-live="polite">${this._range()}</h2>
          <button class="round" @click=${()=>this._go(1)} ?disabled=${t.current_week} aria-label=${e("history.next")} title=${e("history.next")}>${Q("next")}</button>
          ${t.current_week?p:o`<button class="outlined" @click=${()=>this._load(void 0)}>${e("history.this_week")}</button>`}
        </div>
        <label class="toggle" for="hnight">
          <input id="hnight" type="checkbox" .checked=${this._showNight}
                 @change=${c=>this._showNight=c.target.checked}> ${e("grid.night")}
        </label>
      </div>
      ${this._renderLegend()}
      ${t.has_history?n?o`<p class="note">${e("history.empty")}</p>`:p:o`<p class="note">${e("history.retention")}</p>`}
      ${l?o`${this._renderStrip()}${this._renderTotals(t.days[this._day??0],this._day??0)}`:o`
        <div class="days">
          <div></div>
          ${t.days.map((c,h)=>o`
            <div class="day ${t.current_week&&c.date===t.today?"today":""}">
              <div>${e.days[h][0]} <span>${Number(c.date.slice(8))}</span></div>
              ${this._renderTotals(c,h)}
            </div>`)}
        </div>`}
      <div class="body ${this._loading?"busy":""}" style="height:${(f-a)*s}px"
           @pointerdown=${this._swipeStart} @pointerup=${this._swipeEnd} @pointercancel=${()=>this._swipe=null}>
        <div class="axis" aria-hidden="true">
          ${i.map(c=>o`<span style="top:${(c-a)*s}px">${c===f?"24:00":m(c)}</span>`)}
        </div>
        <div class="cols ${l?"single":""}" style="--hour:${60*s}px">
          ${d.map(c=>this._renderColumn(t.days[c],c,a,s))}
        </div>
      </div>
      ${this._pop?this._renderPop():p}`}static styles=$`
    :host { display: block; position: relative; }
    button { font: inherit; color: inherit; }
    .ico { width: 16px; height: 16px; display: block; }
    .state { padding: 24px 0; color: var(--zp-muted); display: grid; gap: 12px; justify-items: start; }
    .head { display: flex; flex-wrap: wrap; gap: 8px 20px; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .nav h2 { margin: 0 6px; font-size: 16px; font-weight: 500; font-variant-numeric: tabular-nums; min-width: 12ch; text-align: center; }
    .round {
      width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--zp-line); background: var(--zp-card);
      display: grid; place-items: center; cursor: pointer; padding: 0;
    }
    .round:disabled { opacity: .35; cursor: default; }
    .outlined { border: 1px solid var(--zp-line); background: var(--zp-card); border-radius: 999px; padding: 6px 12px; cursor: pointer; }
    .filled { border: 0; border-radius: 999px; padding: 8px 16px; cursor: pointer; background: var(--zp-primary); color: var(--zp-primary-ink); }
    .toggle { display: inline-flex; align-items: center; gap: 6px; color: var(--zp-muted); cursor: pointer; white-space: nowrap; }
    .toggle input { accent-color: var(--zp-primary); margin: 0; }
    .note { margin: 4px 0 10px; color: var(--zp-muted); }

    .legend { list-style: none; margin: 0 0 12px; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 16px; color: var(--zp-ink); font-size: 13px; }
    .legend li { display: inline-flex; align-items: center; gap: 6px; }
    .legend li.deleted { color: var(--zp-muted); }
    .swatch {
      width: 14px; height: 14px; border-radius: 4px; background: color-mix(in srgb, var(--c) 30%, var(--zp-card));
      border: 1px solid color-mix(in srgb, var(--c) 75%, var(--zp-card));
    }
    .swatch.powered, .session.powered {
      --c: var(--zp-muted);
      background: repeating-linear-gradient(135deg, color-mix(in srgb, var(--c) 28%, var(--zp-card)) 0 4px, var(--zp-card) 4px 8px);
      border-style: dashed;
    }
    .mark-icon { display: inline-grid; place-items: center; width: 20px; height: 20px; border-radius: 50%; }

    .days, .body { display: grid; grid-template-columns: 2.9rem 1fr; }
    .days { grid-template-columns: 2.9rem repeat(7, minmax(0, 1fr)); position: sticky; top: 0; z-index: 3; background: var(--zp-card); padding-block: 4px 8px; }
    .day { text-align: center; font-weight: 600; font-size: 13px; }
    .day > div > span { color: var(--zp-muted); font-weight: 500; }
    .day.today { color: var(--zp-primary); }
    .day.today > div > span { color: inherit; }

    .totals { list-style: none; margin: 4px 0 0; padding: 0; display: flex; flex-direction: column; gap: 3px; align-items: stretch; }
    .totals li {
      display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; column-gap: 4px;
      padding: 1px 6px; border-radius: 8px; font-size: 12px; font-weight: 500; line-height: 1.35; text-align: start;
      color: var(--zp-ink); background: color-mix(in srgb, var(--c) 18%, var(--zp-card));
      border-inline-start: 4px solid var(--c); min-width: 0; cursor: default;
    }
    .totals li .who { overflow-wrap: anywhere; min-width: 0; }
    .totals li strong { font-weight: 600; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .totals li.deleted { color: var(--zp-muted); border-inline-start-style: dashed; }
    .totals li:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 1px; }
    .strip + .totals { flex-direction: row; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; }
    .strip + .totals li { font-size: 13px; padding: 2px 8px; }
    .legend .week-total { color: var(--zp-muted); font-variant-numeric: tabular-nums; }

    .strip { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 10px; }
    .strip button {
      border: 1px solid var(--zp-line); background: var(--zp-card); border-radius: 12px; padding: 6px 0 4px; cursor: pointer;
      display: grid; justify-items: center; gap: 1px; font-size: 12px; color: var(--zp-muted);
    }
    .strip strong { font-size: 15px; color: var(--zp-ink); font-variant-numeric: tabular-nums; }
    .strip button.today strong { color: var(--zp-primary); }
    .strip button[aria-selected="true"] { border-color: var(--zp-primary); box-shadow: inset 0 0 0 1px var(--zp-primary); }
    .strip .dot { width: 5px; height: 5px; border-radius: 50%; background: transparent; }
    .strip .dot.on { background: var(--zp-primary); }

    .body { position: relative; margin-top: 4px; touch-action: pan-y; }
    .body.busy { opacity: .6; transition: opacity .2s; }
    .axis { position: relative; }
    .axis span { position: absolute; right: 8px; transform: translateY(-50%); font-size: 11px; color: var(--zp-muted); font-variant-numeric: tabular-nums; }
    .cols {
      position: relative; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));
      border-top: 1px solid var(--zp-line); border-left: 1px solid var(--zp-line);
      background-image: linear-gradient(var(--zp-line) 1px, transparent 1px), linear-gradient(var(--zp-line-soft) 1px, transparent 1px);
      background-size: 100% var(--hour), 100% calc(var(--hour) / 2);
    }
    .cols.single { grid-template-columns: minmax(0, 1fr); }
    .col { position: relative; border-right: 1px solid var(--zp-line); --lane: 24px; }
    .cols.single .col { --lane: 34px; }
    .col.today { background-color: color-mix(in srgb, var(--zp-primary) 5%, transparent); }
    .now { position: absolute; left: -1px; right: 0; height: 2px; background: var(--zp-danger); pointer-events: none; z-index: 4; }
    .now::before { content: ""; position: absolute; left: -4px; top: -3px; width: 8px; height: 8px; border-radius: 50%; background: var(--zp-danger); }

    .band { position: absolute; left: 0; right: 0; pointer-events: none; z-index: 0; }
    .band.plug_lost { background: repeating-linear-gradient(45deg, color-mix(in srgb, var(--zp-warn) 22%, transparent) 0 3px, transparent 3px 9px); }
    .band.keypad_offline { background: repeating-linear-gradient(-45deg, color-mix(in srgb, var(--zp-warn) 16%, transparent) 0 2px, transparent 2px 10px); }
    .band.control_off { background: color-mix(in srgb, var(--zp-muted) 12%, transparent); }
    .band.ha_down { background: repeating-linear-gradient(90deg, color-mix(in srgb, var(--zp-muted) 20%, transparent) 0 2px, transparent 2px 8px); }

    .session {
      position: absolute; left: 3px; right: calc(var(--lane) + 2px); box-sizing: border-box; border-radius: 6px; overflow: hidden; z-index: 1;
      padding: 0; text-align: left; cursor: pointer;
      background: color-mix(in srgb, var(--c) 26%, var(--zp-card)); border: 1px solid color-mix(in srgb, var(--c) 75%, var(--zp-card));
      border-left-width: 4px; color: var(--zp-ink); display: flex; align-items: flex-start;
    }
    .session.deleted { border-style: dashed; border-left-style: solid; color: var(--zp-muted); }
    .session.ongoing { border-bottom: 2px dashed var(--c); }
    .session.thin { border-width: 1px; border-left-width: 3px; }
    .session:hover { box-shadow: 0 2px 8px rgb(0 0 0 / .14); }
    .label { padding: 2px 5px; font-size: 11.5px; line-height: 1.2; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; pointer-events: none; }
    .label small { display: block; font-weight: 500; color: var(--zp-muted); font-variant-numeric: tabular-nums; }

    .mark {
      position: absolute; right: calc((var(--lane) - 20px) / 2); width: 20px; height: 20px; border-radius: 50%; padding: 0; z-index: 2;
      display: grid; place-items: center; cursor: pointer; border: 1px solid currentColor; background: var(--zp-card);
    }
    .mark .ico { width: 13px; height: 13px; }
    .mark .count {
      position: absolute; top: -7px; right: -7px; min-width: 15px; padding: 0 3px; box-sizing: border-box; border-radius: 8px;
      font-size: 9.5px; font-weight: 700; line-height: 14px; background: currentColor; text-align: center;
    }
    .mark .count { color: var(--zp-card); background: var(--mark-c); }
    .mark.denied, .mark-icon.denied, .mark.lockout, .mark-icon.lockout { color: var(--zp-danger); --mark-c: var(--zp-danger); }
    .mark.bypass, .mark-icon.bypass, .mark.plug_lost, .mark-icon.plug_lost, .mark.keypad_offline, .mark-icon.keypad_offline { color: var(--zp-warn); --mark-c: var(--zp-warn); }
    .mark.standby, .mark-icon.standby { color: #5c7ea8; --mark-c: #5c7ea8; }
    .mark.control_off, .mark-icon.control_off, .mark.ha_down, .mark-icon.ha_down { color: var(--zp-muted); --mark-c: var(--zp-muted); }
    .mark-icon .ico { width: 15px; height: 15px; }

    button:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 2px; z-index: 5; }
    .backdrop { position: fixed; inset: 0; z-index: 9; }
    .pop {
      position: absolute; z-index: 10; width: 280px; box-sizing: border-box; padding: 12px 14px; border-radius: 12px;
      background: var(--zp-raised); border: 1px solid var(--zp-line); box-shadow: var(--zp-shadow); display: grid; gap: 4px;
    }
    .pop.hover { pointer-events: none; }
    .pop h3 { margin: 0 0 2px; font-size: 14px; }
    .pop p { margin: 0; font-size: 13px; color: var(--zp-muted); font-variant-numeric: tabular-nums; }
    @media (max-width: 639px) {
      .days, .body { grid-template-columns: 2.4rem 1fr; }
      .axis span { font-size: 10px; right: 5px; }
      .backdrop { background: rgb(0 0 0 / .35); }
      .pop {
        position: fixed; left: 0 !important; right: 0; top: auto !important; bottom: 0; width: auto;
        border-radius: 18px 18px 0 0; padding: 16px 18px calc(18px + env(safe-area-inset-bottom, 0px));
      }
      .pop.hover { display: none; }
    }
    @media (hover: none) { .pop.hover { display: none; } }
    @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
  `};customElements.define("zapette-history",be);var Y=r=>JSON.parse(JSON.stringify(r)),Ct=(r,e)=>JSON.stringify(r)===JSON.stringify(e),F="__manual__",ve="",Tt=["identity","plug","plug_behavior","keypad","keypad_guard","sessions"],Ge=["standby_cut"],Mt=r=>{history.pushState(null,"",r),window.dispatchEvent(new CustomEvent("location-changed",{detail:{replace:!1}}))},xe=class extends y{static properties={hass:{attribute:!1},entryId:{attribute:!1},t:{attribute:!1},_data:{state:!0},_drafts:{state:!0},_errors:{state:!0},_busy:{state:!0},_loadError:{state:!0},_candidates:{state:!0},_searching:{state:!0},_manual:{state:!0},_test:{state:!0},_dialog:{state:!0},_dialogError:{state:!0}};constructor(){super(),this._data=null,this._drafts={},this._errors={},this._busy={},this._candidates=null,this._manual=!1,this._test=null,this._dialog=null,this._wasDirty=!1}disconnectedCallback(){this._stopTest(),super.disconnectedCallback()}willUpdate(e){e.has("entryId")&&this.entryId&&this._load()}updated(){let e=this.dirty;e!==this._wasDirty&&(this._wasDirty=e,this.dispatchEvent(new CustomEvent("dirty-changed",{detail:e,bubbles:!0,composed:!0})))}get dirty(){return Tt.some(e=>this._isDirty(e))}_isDirty(e){return!!this._data&&!!this._drafts[e]&&!Ct(this._drafts[e],this._data.values[e])}discard(){this._data&&(this._drafts=Y(this._data.values)),this._errors={},this._manual=this._isManualTopic(this._data?.values.keypad.keypad_topic)}async _load(){this._stopTest(),this._data=null,this._loadError=null,this._candidates=null;try{let e=await this.hass.callWS({type:"zapette/settings",entry_id:this.entryId});this._data=e,this._drafts=Y(e.values),this._errors={},this._manual=!1,this._searchKeypads()}catch(e){this._loadError=e.message??String(e)}}_toast(e,t="info"){this.dispatchEvent(new CustomEvent("toast",{detail:{text:e,kind:t},bubbles:!0,composed:!0}))}_errorText(e){let t=this.t(`error.${e.code}`);return t===`error.${e.code}`?e.message??String(e):t}_set(e,t,s){this._drafts={...this._drafts,[e]:{...this._drafts[e],[t]:s}},this._errors[e]&&(this._errors={...this._errors,[e]:null})}_schema(e){return this._data.schema[e]??[]}_fieldError(e,t){return e.type!=="int"?null:Number.isInteger(t)?t<e.min||t>e.max?this.t("settings.range",{min:e.min,max:e.max}):null:this.t("settings.integer")}_localErrors(e){return this._schema(e).some(t=>this._fieldError(t,this._drafts[e]?.[t.key]))}async _save(e){this._busy={...this._busy,[e]:!0};try{let t=Y(this._drafts[e]);e==="plug"&&!t.power_entity&&(t.power_entity=null);let s=await this.hass.callWS({type:"zapette/settings/update",entry_id:this.entryId,section:e,values:t}),a={...this._drafts,[e]:Y(s.values[e])};this._data=s,this._drafts=a,this._errors={...this._errors,[e]:null},e==="keypad"&&(this._manual=this._isManualTopic(s.values.keypad.keypad_topic)),e==="identity"&&this.dispatchEvent(new CustomEvent("renamed",{detail:{title:s.title},bubbles:!0,composed:!0})),this._toast(this.t("settings.saved",{section:this.t(`settings.s_${e}`)}),"ok")}catch(t){this._errors={...this._errors,[e]:{field:t.message,text:this._errorText(t)}}}finally{this._busy={...this._busy,[e]:!1}}}_cancel(e){this._drafts={...this._drafts,[e]:Y(this._data.values[e])},this._errors={...this._errors,[e]:null},e==="keypad"&&(this._manual=this._isManualTopic(this._data.values.keypad.keypad_topic))}_state(e){let t=this._data?.status.entities[e];return t?this.hass.states?.[t]??null:null}_when(e,t=!0){let s=new Date(e);if(Number.isNaN(s.getTime()))return this.t("settings.unknown");let a=t?{dateStyle:"short",timeStyle:"short"}:{timeStyle:"short"};return new Intl.DateTimeFormat(this.t.lang,{...a,timeZone:this.hass.config?.time_zone}).format(s)}async _toggleControl(e){let t=this._data.status.entities.control_active;try{await this.hass.callService("switch",e.target.checked?"turn_on":"turn_off",{entity_id:t})}catch(s){e.target.checked=!e.target.checked,this._toast(this._errorText(s),"error")}}async _unblock(){try{await this.hass.callService("zapette","unblock_keypad",{config_entry_id:this.entryId}),this._toast(this.t("settings.unblocked"),"ok")}catch(e){this._toast(this._errorText(e),"error")}}_isManualTopic(e){return!!e&&!(this._candidates?.keypads??[]).some(t=>t.topic===e)}async _searchKeypads(){this._searching=!0;try{this._candidates=await this.hass.callWS({type:"zapette/keypad/candidates",entry_id:this.entryId})}catch{this._candidates={mqtt:!1,keypads:[]}}finally{this._searching=!1,this._manual=this._isManualTopic(this._drafts.keypad?.keypad_topic)}}_chooseKeypad(e){let t=e.target.value;this._manual=t===F,t!==F&&this._set("keypad","keypad_topic",t||null),this._stopTest(),this._test=null}async _startTest(){let e=this._drafts.keypad.keypad_topic;if(e){this._stopTest(),this._test={status:"waiting",topic:e};try{this._unsubTest=await this.hass.connection.subscribeMessage(t=>{this._unsubTest=null,this._test={...t,topic:e}},{type:"zapette/keypad/test",entry_id:this.entryId,topic:e})}catch(t){this._test={status:"error",text:this._errorText(t),topic:e}}}}_stopTest(){let e=this._unsubTest;this._unsubTest=null,e&&Promise.resolve(e()).catch(()=>{}),this._test?.status==="waiting"&&(this._test=null)}_openParent(e,t=null){this._dialog={mode:e,parent:t},this._dialogError=null,this.updateComplete.then(()=>{let s=this.renderRoot.querySelector("#parent-dialog"),a=s.querySelector("form").elements;a.namedItem("pname")&&(a.namedItem("pname").value=t?.name??"",a.namedItem("code").value="",a.namedItem("confirm").value=""),s.showModal()})}_closeParent(){this.renderRoot.querySelector("#parent-dialog")?.close(),this._dialog=null}async _submitParent(e){e.preventDefault();let t=e.target.elements,{mode:s,parent:a}=this._dialog,i={entry_id:this.entryId};if(s==="delete")Object.assign(i,{type:"zapette/parent/delete",parent_id:a.id});else{let n=t.namedItem("code"),l=t.namedItem("confirm");Object.assign(i,{name:t.namedItem("pname").value,code:n.value,code_confirm:l.value}),s==="add"?i.type="zapette/parent/add":Object.assign(i,{type:"zapette/parent/update",parent_id:a.id}),n.value="",l.value=""}try{let n=await this.hass.callWS(i);this._data={...this._data,parents:n.parents};let l=s==="delete"?a.name:i.name.trim();this._closeParent(),this._toast(this.t(`settings.parent_${{add:"added",edit:"updated",delete:"deleted"}[s]}`,{name:l}),"ok")}catch(n){this._dialogError=this._errorText(n)}}_sectionCard(e,t,{dev:s=null}={}){let a=this.t,i=this._isDirty(e),n=this._busy[e],l=this._errors[e];return o`
      <section class="card" aria-labelledby="h-${e}">
        <h2 id="h-${e}">${a(`settings.s_${e}`)}</h2>
        <fieldset ?disabled=${n}>${t}</fieldset>
        ${s??p}
        ${l?o`<p class="error" role="alert">${l.text}</p>`:p}
        <div class="actions">
          <span class="grow"></span>
          <button class="text" ?disabled=${!i||n} @click=${()=>this._cancel(e)}>${a("settings.cancel")}</button>
          <button class="filled" ?disabled=${!i||n||this._localErrors(e)} @click=${()=>this._save(e)}>
            ${a(n?"settings.saving":"settings.save")}
          </button>
        </div>
      </section>`}_field(e,t){let s=this.t,a=this._drafts[e]?.[t.key],i=`f-${t.key}`,n=s(`settings.h.${t.key}`),l=n===`settings.h.${t.key}`?null:n,d=this._errors[e]?.field===t.key;if(t.type==="bool")return o`
        <div class="row">
          <label class="switch" for=${i}>
            <input id=${i} type="checkbox" role="switch" .checked=${!!a}
                   @change=${h=>this._set(e,t.key,h.target.checked)}>
            <span class="track"><span class="thumb"></span></span>
            <span>${s(`settings.f.${t.key}`)}</span>
          </label>
          ${l?o`<p class="help">${l}</p>`:p}
        </div>`;if(t.type==="choice")return o`
        <label class="row" for=${i}>
          <span class="label">${s(`settings.f.${t.key}`)}</span>
          <select id=${i} class=${d?"invalid":""} @change=${h=>this._set(e,t.key,h.target.value)}>
            ${t.choices.map(h=>o`<option value=${h} ?selected=${h===a}>${s(`settings.off_key.${h}`)}</option>`)}
          </select>
          ${l?o`<span class="help">${l}</span>`:p}
        </label>`;let c=this._fieldError(t,a);return o`
      <label class="row" for=${i}>
        <span class="label">${s(`settings.f.${t.key}`)}</span>
        <span class="number">
          <input id=${i} type="number" inputmode="numeric" min=${t.min} max=${t.max} step="1"
                 class=${c||d?"invalid":""} aria-invalid=${c||d?"true":"false"}
                 .value=${a==null?"":String(a)}
                 @input=${h=>this._set(e,t.key,h.target.value===""?"":Number(h.target.value))}>
          ${t.unit?o`<span class="unit">${t.unit}</span>`:p}
        </span>
        <span class="help ${c?"bad":""}">${c??l??s("settings.range",{min:t.min,max:t.max})}</span>
      </label>`}_optionSection(e){let t=this._schema(e),s=t.filter(i=>Ge.includes(i.key)),a=t.filter(i=>!Ge.includes(i.key));return this._sectionCard(e,o`
        <div class="fields">${a.map(i=>this._field(e,i))}</div>
        ${s.length?o`
          <div class="dev">
            <h3>${this.t("settings.dev")}</h3>
            ${s.map(i=>this._field(e,i))}
          </div>`:p}`)}_renderStatus(){let e=this.t,t=this._data.status;if(!t.loaded)return o`<section class="card status"><h2>${e("settings.status")}</h2><p class="muted">${e("settings.status_unavailable")}</p></section>`;let s=this._state("control_active"),a=this._state("plug_reachable"),i=this._state("plug_problem"),n=this._state("last_outage"),l=this._state("keypad_available"),d=this._state("keypad_battery"),c=this._state("keypad_locked"),h=!!t.entities.plug_reachable,_=!!t.entities.keypad_available,u=d&&!Number.isNaN(Number(d.state))?Number(d.state):null,g=v=>o`<span class="dot ${v}" aria-hidden="true"></span>`;return o`
      <section class="card status" aria-labelledby="h-status">
        <h2 id="h-status">${e("settings.status")}</h2>
        ${s?o`
          <div class="row">
            <label class="switch" for="control">
              <input id="control" type="checkbox" role="switch" .checked=${s.state==="on"} @change=${this._toggleControl}>
              <span class="track"><span class="thumb"></span></span>
              <span>${e("settings.control")}</span>
            </label>
            <p class="help">${e("settings.control_help")}</p>
          </div>`:p}
        <div class="grid">
          <div class="item">
            <h3>${e("settings.plug")}</h3>
            ${h?o`
              <p>${a?.state==="on"?o`${g("ok")}${e("settings.reachable")}`:o`${g("bad")}${e("settings.unreachable")}`}</p>
              ${i?.state==="on"?o`<p>${g("warn")}${e("settings.problem")}</p>`:p}
              <p class="muted">${n&&n.state&&!["unknown","unavailable"].includes(n.state)?e("settings.last_outage",{when:this._when(n.state)}):e("settings.no_outage")}</p>
              ${n?.attributes?.outages_24h!=null?o`<p class="muted">${e("settings.outages_24h",{n:n.attributes.outages_24h})}</p>`:p}
            `:o`<p class="muted">${e("settings.plug_none")}</p>`}
          </div>
          <div class="item">
            <h3>${e("settings.keypad")}</h3>
            ${_?o`
              <p>${l?.state==="off"?o`${g("bad")}${e("settings.unavailable")}`:l?.state==="on"?o`${g("ok")}${e("settings.available")}`:o`${g("")}${e("settings.unknown")}`}</p>
              ${u!=null?o`<p class=${u<15?"bad-text":"muted"}>${e(u<15?"settings.battery_low":"settings.battery",{level:u})}</p>`:p}
              ${c?.state==="on"?o`
                <p>${g("warn")}${e("settings.locked",{until:c.attributes?.until?this._when(c.attributes.until,!1):"\u2026"})}</p>
                <button class="outlined" @click=${this._unblock}>${e("settings.unblock")}</button>
              `:o`<p class="muted">${e("settings.not_locked")}</p>`}
            `:o`<p class="muted">${e("settings.keypad_none")}</p>`}
          </div>
        </div>
        ${t.device_id?o`
          <button class="link" @click=${()=>Mt(`/config/devices/device/${t.device_id}`)}>${e("settings.open_device")}</button>`:p}
      </section>`}_renderIdentity(){let e=this.t,t=this._errors.identity;return this._sectionCard("identity",o`
      <label class="row" for="tv-name">
        <span class="label">${e("settings.tv_name")}</span>
        <input id="tv-name" type="text" maxlength="30" autocomplete="off" class=${t?"invalid":""}
               .value=${this._drafts.identity?.tv_name??""} @input=${s=>this._set("identity","tv_name",s.target.value)}>
        <span class="help">${e("settings.tv_name_help")}</span>
      </label>`)}_renderParents(){let e=this.t,t=this._data.parents,s=t.length<=1;return o`
      <section class="card" aria-labelledby="h-parents">
        <h2 id="h-parents">${e("settings.s_parents")}</h2>
        <p class="help">${e("settings.parents_help")}</p>
        <ul class="parents">
          ${t.map(a=>o`
            <li>
              <span class="pname">${a.name}</span>
              <button class="text" @click=${()=>this._openParent("edit",a)}>${e("settings.edit_parent")}</button>
              <button class="text danger" ?disabled=${s} title=${s?e("settings.last_parent"):""}
                      @click=${()=>this._openParent("delete",a)}>${e("settings.delete_parent")}</button>
            </li>`)}
        </ul>
        ${s?o`<p class="help">${e("settings.last_parent")}</p>`:p}
        <div class="actions"><button class="outlined" @click=${()=>this._openParent("add")}>${e("settings.add_parent")}</button></div>
      </section>`}_entityOptions(e,t){let s=Object.values(this.hass.states??{}).filter(e);s.sort((i,n)=>(i.attributes.friendly_name??i.entity_id).localeCompare(n.attributes.friendly_name??n.entity_id));let a=s.map(i=>({value:i.entity_id,label:`${i.attributes.friendly_name??i.entity_id} (${i.entity_id})`}));return t&&!a.some(i=>i.value===t)&&a.unshift({value:t,label:this.t("settings.missing",{entity:t})}),a}_renderPlug(){let e=this.t,t=this._drafts.plug??{},s=new Set(Object.values(this._data.status.entities).filter(Boolean)),a=this._entityOptions(l=>l.entity_id.startsWith("switch.")&&!l.entity_id.startsWith("switch.zapette")&&!s.has(l.entity_id),t.plug_entity),i=this._entityOptions(l=>l.entity_id.startsWith("sensor.")&&l.attributes.device_class==="power"&&!l.entity_id.startsWith("sensor.zapette"),t.power_entity),n=this._errors.plug?.field;return this._sectionCard("plug",o`
      <label class="row" for="plug-entity">
        <span class="label">${e("settings.plug_entity")}</span>
        <select id="plug-entity" class=${n==="plug_entity"?"invalid":""} @change=${l=>this._set("plug","plug_entity",l.target.value)}>
          ${t.plug_entity?p:o`<option value="" selected></option>`}
          ${a.map(l=>o`<option value=${l.value} ?selected=${l.value===t.plug_entity}>${l.label}</option>`)}
        </select>
      </label>
      <label class="row" for="power-entity">
        <span class="label">${e("settings.power_entity")}</span>
        <select id="power-entity" class=${n==="power_entity"?"invalid":""} @change=${l=>this._set("plug","power_entity",l.target.value||null)}>
          <option value="" ?selected=${!t.power_entity}>${e("settings.power_none")}</option>
          ${i.map(l=>o`<option value=${l.value} ?selected=${l.value===t.power_entity}>${l.label}</option>`)}
        </select>
      </label>
      <p class="note">${e("settings.plug_note")}</p>`)}_renderKeypad(){let e=this.t,t=this._drafts.keypad?.keypad_topic??null,s=this._candidates?.keypads??[],a=this._manual?F:t??ve,i=this._test,n=i?.status==="waiting",l=p;if(i&&i.topic===t){let d={waiting:e("settings.keypad_test_wait",{topic:t}),key:e("settings.keypad_test_key",{key:i.key}),timeout:e("settings.keypad_test_timeout",{seconds:i.seconds}),no_mqtt:e("settings.keypad_test_no_mqtt"),error:i.text}[i.status];l=o`<p class="test ${i.status}" role="status" aria-live="polite">${d}</p>`}return this._sectionCard("keypad",o`
      <label class="row" for="keypad-choice">
        <span class="label">${e("settings.keypad_choice")}</span>
        <select id="keypad-choice" @change=${this._chooseKeypad}>
          <option value=${ve} ?selected=${a===ve}>${e("settings.keypad_none")}</option>
          ${s.map(d=>o`<option value=${d.topic} ?selected=${a===d.topic}>${d.label}</option>`)}
          <option value=${F} ?selected=${a===F}>${e("settings.keypad_manual")}</option>
        </select>
        <span class="help">
          ${this._searching?e("settings.keypad_searching"):this._candidates&&!this._candidates.mqtt?e("settings.keypad_no_mqtt"):this._candidates?e("settings.keypad_found",{n:s.length}):""}
        </span>
      </label>
      ${this._manual?o`
        <label class="row" for="keypad-topic">
          <span class="label">${e("settings.keypad_topic")}</span>
          <input id="keypad-topic" type="text" autocomplete="off" spellcheck="false" placeholder="zigbee2mqtt/mon_clavier"
                 class=${this._errors.keypad?"invalid":""}
                 .value=${t??""} @input=${d=>{this._set("keypad","keypad_topic",d.target.value.trim()||null),this._test=null}}>
        </label>`:p}
      <div class="actions left">
        <button class="outlined" ?disabled=${this._searching} @click=${this._searchKeypads}>${e("settings.keypad_search")}</button>
        ${n?o`<button class="outlined" @click=${()=>this._stopTest()}>${e("settings.cancel")}</button>`:o`<button class="outlined" ?disabled=${!t} @click=${this._startTest}>
              ${i&&i.topic===t&&i.status!=="key"?e("settings.keypad_test_retry"):e("settings.keypad_test")}</button>`}
      </div>
      ${l}`)}_renderParentDialog(){let e=this.t,t=this._dialog,s=t?t.mode==="add"?e("settings.parent_title_add"):t.mode==="edit"?e("settings.parent_title_edit",{name:t.parent.name}):e("settings.delete_parent_title",{name:t.parent.name}):"";return o`
      <dialog id="parent-dialog" aria-labelledby="parent-title" @close=${()=>this._dialog=null}>
        <form @submit=${this._submitParent} novalidate>
          <h2 id="parent-title">${s}</h2>
          ${t?.mode==="delete"?o`<p class="note">${e("settings.delete_parent_text")}</p>`:o`
            <label for="p-name">${e("settings.parent_name")}
              <input id="p-name" name="pname" type="text" maxlength="30" autocomplete="off" required>
            </label>
            <label for="p-code">${e("panel.code")}
              <input id="p-code" name="code" type="password" inputmode="numeric" autocomplete="off" ?required=${t?.mode==="add"}>
            </label>
            <label for="p-confirm">${e("panel.confirm")}
              <input id="p-confirm" name="confirm" type="password" inputmode="numeric" autocomplete="off" ?required=${t?.mode==="add"}>
            </label>
            <p class="note">${t?.mode==="edit"?e("settings.keep_code"):e("panel.code_note")}</p>`}
          ${this._dialogError?o`<p class="error" role="alert">${this._dialogError}</p>`:p}
          <div class="actions">
            <span class="grow"></span>
            <button type="button" class="text" @click=${this._closeParent}>${e("settings.cancel")}</button>
            <button type="submit" class="filled ${t?.mode==="delete"?"danger":""}">
              ${t?.mode==="delete"?e("settings.delete"):e("panel.validate")}</button>
          </div>
        </form>
      </dialog>`}render(){let e=this.t;return this._loadError?o`<section class="card"><p class="error">${e("settings.load_error",{message:this._loadError})}</p></section>`:this._data?o`
      <div class="stack">
        ${this._renderStatus()}
        ${this._renderIdentity()}
        ${this._renderParents()}
        ${this._renderPlug()}
        ${this._optionSection("plug_behavior")}
        ${this._renderKeypad()}
        ${this._optionSection("keypad_guard")}
        ${this._optionSection("sessions")}
      </div>
      ${this._renderParentDialog()}`:o`<div class="loading" aria-busy="true"></div>`}static styles=$`
    :host { display: block; }
    .stack { display: grid; gap: 16px; max-width: 760px; }
    .loading { height: 30vh; }
    .card {
      background: var(--zp-card); border: 1px solid var(--zp-line); border-radius: var(--ha-card-border-radius, 12px);
      padding: 18px; box-shadow: var(--ha-card-box-shadow, none); min-width: 0;
    }
    h2 { margin: 0 0 12px; font-size: 17px; font-weight: 500; }
    h3 { margin: 0 0 6px; font-size: 13px; font-weight: 600; color: var(--zp-muted); text-transform: uppercase; letter-spacing: .04em; }
    p { margin: 0; }
    fieldset { border: 0; margin: 0; padding: 0; min-width: 0; display: grid; gap: 14px; }
    .fields { display: grid; gap: 14px; }
    .row { display: grid; gap: 4px; min-width: 0; }
    .label { font-weight: 500; }
    .help, .muted, .note { color: var(--zp-muted); font-size: 13px; line-height: 1.4; }
    .help.bad, .bad-text { color: var(--zp-danger); }
    .note { margin-top: 2px; }
    input[type="text"], input[type="number"], select {
      border: 1px solid var(--zp-line); border-radius: 8px; padding: 8px 10px; background: var(--zp-card); color: var(--zp-ink);
      font-size: 15px; min-width: 0; max-width: 100%; box-sizing: border-box;
    }
    input[type="text"], select { width: 100%; }
    .number { display: inline-flex; align-items: center; gap: 8px; }
    .number input { width: 110px; }
    .unit { color: var(--zp-muted); }
    .invalid { border-color: var(--zp-danger) !important; }
    .dev { margin-top: 6px; padding: 12px; border: 1px dashed var(--zp-warn); border-radius: 10px; background: var(--zp-warn-bg); display: grid; gap: 10px; }
    .dev h3 { color: var(--zp-ink); }
    .actions { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 14px; }
    .actions.left { margin-top: 0; }
    .grow { flex: 1; }
    .error { color: var(--zp-danger); font-size: 13px; margin-top: 10px; }
    .status .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 14px 0 10px; }
    .status .item { display: grid; gap: 4px; align-content: start; }
    .status .item button { justify-self: start; margin-top: 6px; }
    .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-inline-end: 8px; background: var(--zp-muted); }
    .dot.ok { background: var(--zp-ok); }
    .dot.bad { background: var(--zp-danger); }
    .dot.warn { background: var(--zp-warn); }
    .parents { list-style: none; margin: 10px 0 0; padding: 0; display: grid; gap: 2px; }
    .parents li { display: flex; align-items: center; gap: 4px; padding: 4px 0; border-bottom: 1px solid var(--zp-line-soft); }
    .pname { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
    .test { margin-top: 12px; padding: 10px 12px; border-radius: 10px; background: var(--zp-line-soft); }
    .test.key { background: color-mix(in srgb, var(--zp-ok) 16%, var(--zp-card)); }
    .test.timeout, .test.no_mqtt, .test.error { background: var(--zp-warn-bg); }

    .switch { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; font-weight: 500; }
    .switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
    .track { flex: none; width: 36px; height: 20px; border-radius: 999px; background: var(--zp-line); position: relative; transition: background .15s; }
    .thumb {
      position: absolute; top: 2px; left: 2px; width: 16px; height: 16px; border-radius: 50%; background: #fff;
      box-shadow: 0 1px 2px rgb(0 0 0 / .3); transition: transform .15s;
    }
    .switch input:checked + .track { background: var(--zp-primary); }
    .switch input:checked + .track .thumb { transform: translateX(16px); }
    .switch input:focus-visible + .track { outline: 2px solid var(--zp-primary); outline-offset: 2px; }

    button { font: inherit; color: inherit; }
    .text, .filled, .outlined { border-radius: 999px; padding: 8px 16px; cursor: pointer; font-weight: 500; }
    .text, .filled { border: 0; }
    .text { background: none; color: var(--zp-primary); }
    .text.danger { color: var(--zp-danger); }
    .filled { background: var(--zp-primary); color: var(--zp-primary-ink); }
    .filled.danger { background: var(--zp-danger); color: #fff; }
    .outlined { border: 1px solid var(--zp-line); background: var(--zp-card); }
    .link { border: 0; background: none; color: var(--zp-primary); cursor: pointer; padding: 4px 0; }
    button:disabled { opacity: .45; cursor: default; }
    button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 2px; }

    dialog {
      border: 1px solid var(--zp-line); border-radius: 18px; padding: 22px; background: var(--zp-raised); color: var(--zp-ink);
      width: min(92vw, 400px); box-sizing: border-box; box-shadow: var(--zp-shadow);
    }
    dialog::backdrop { background: rgb(0 0 0 / .4); }
    dialog form { display: grid; gap: 12px; }
    dialog h2 { margin: 0; font-size: 18px; }
    dialog label { display: grid; gap: 4px; font-size: 12.5px; color: var(--zp-muted); }
    dialog input { border: 1px solid var(--zp-line); border-radius: 8px; padding: 9px 10px; background: var(--zp-card); color: var(--zp-ink); font-size: 16px; }
    dialog input[type="password"] { letter-spacing: .2em; }
    dialog .actions { margin-top: 4px; }

    @media (max-width: 599px) {
      .card { padding: 14px; }
      dialog { width: 100vw; max-width: 100vw; height: 100dvh; max-height: 100dvh; margin: 0; border-radius: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; }
    }
  `};customElements.define("zapette-settings",xe);var $e=class extends y{static properties={rules:{attribute:!1},t:{attribute:!1},fine:{state:!0},showNight:{state:!0},pop:{state:!0}};constructor(){super(),this.fine=!1,this.showNight=!1,this.pop=null,this.drag=null,this._onResize=()=>this.requestUpdate()}connectedCallback(){super.connectedCallback(),window.addEventListener("resize",this._onResize)}disconnectedCallback(){window.removeEventListener("resize",this._onResize),super.disconnectedCallback()}get _px(){return window.innerWidth<640?.62:.8}get _step(){return this.fine?5:15}get _top(){if(this.showNight)return 0;let e=Math.min(360,...this.rules.slots.flat().map(t=>t[0]));return Math.floor(e/60)*60}_snap(e){return Math.round(e/this._step)*this._step}_edit(e,t,s){this.dispatchEvent(new CustomEvent("edit",{detail:{mutate:e,info:t,params:s},bubbles:!0,composed:!0}))}_commit({day:e,idx:t},s){this._focusAfter={day:s.day,start:s.start},this._edit(a=>(t!=null&&a.slots[e].splice(t,1),s.end-s.start<ge?{error:"slot_too_short"}:B(a,s.day,[s.start,s.end])))}_pos(e){let t=this.renderRoot.querySelector(".cols").getBoundingClientRect();return{m:x(this._top+(e.clientY-t.top)/this._px,0,f),day:x(Math.floor((e.clientX-t.left)/(t.width/7)),0,6)}}_down(e){if(e.button!==0)return;let{m:t,day:s}=this._pos(e),a=e.target.closest(".slot:not(.preview)"),i=e.pointerType==="touch";if(a){let n=+a.dataset.day,l=+a.dataset.idx,d=e.target.dataset.handle;this.drag={mode:d?`resize-${d}`:"move",day:n,idx:l,orig:this.rules.slots[n][l],origin:t,x0:e.clientX,y0:e.clientY,el:a},e.currentTarget.setPointerCapture(e.pointerId),e.preventDefault(),a.focus({preventScroll:!0})}else this.drag={mode:"create",day:s,idx:null,origin:this._snap(t),x0:e.clientX,y0:e.clientY,touch:i},i||(e.currentTarget.setPointerCapture(e.pointerId),e.preventDefault())}_move(e){let t=this.drag;if(!t||!t.moved&&Math.hypot(e.clientX-t.x0,e.clientY-t.y0)<5)return;if(t.mode==="create"&&t.touch){this.drag=null;return}t.moved=!0;let{m:s,day:a}=this._pos(e),i=this._step;if(t.mode==="create"){let n=this._snap(s),l=Math.min(t.origin,n),d=Math.max(Math.max(t.origin,n),l+i);t.preview={day:t.day,start:l,end:Math.min(d,f)}}else if(t.mode==="move"){let n=t.orig[1]-t.orig[0],l=x(t.orig[0]+Math.round((s-t.origin)/i)*i,0,f-n);t.preview={day:a,start:l,end:l+n}}else t.mode==="resize-start"?t.preview={day:t.day,start:x(this._snap(s),0,t.orig[1]-i),end:t.orig[1]}:t.preview={day:t.day,start:t.orig[0],end:x(this._snap(s),t.orig[0]+i,f)};this.requestUpdate()}_up(){let e=this.drag;if(e){if(this.drag=null,e.moved)e.preview&&this._commit(e,e.preview);else if(e.idx!=null)this._openSlot(e.el,e.day,e.idx);else{let t=x(e.origin,0,f-60);this._focusAfter={day:e.day,start:t},this._edit(s=>B(s,e.day,[t,t+60]),"slot_added",{day:e.day})}this.requestUpdate()}}_cancel(){this.drag=null,this.requestUpdate()}_slotKey(e,t,s){let[a,i]=this.rules.slots[t][s],n=this._step,l=null;if(e.key==="Enter"||e.key===" "){e.preventDefault(),this._openSlot(e.currentTarget,t,s);return}if(e.key==="Delete"||e.key==="Backspace"){e.preventDefault(),this._edit(d=>{d.slots[t].splice(s,1)},"slot_deleted");return}if(e.key==="ArrowUp"||e.key==="ArrowDown"){let d=e.key==="ArrowUp"?-n:n;if(e.shiftKey)l={day:t,start:a,end:x(i+d,a+n,f)};else{let c=x(a+d,0,f-(i-a));l={day:t,start:c,end:c+i-a}}}(e.key==="ArrowLeft"||e.key==="ArrowRight")&&(l={day:x(t+(e.key==="ArrowLeft"?-1:1),0,6),start:a,end:i}),l&&(e.preventDefault(),this._commit({day:t,idx:s},l))}updated(){if(!this._focusAfter)return;let{day:e,start:t}=this._focusAfter;this._focusAfter=null,[...this.renderRoot.querySelectorAll(".slot:not(.preview)")].find(a=>+a.dataset.day===e&&+a.dataset.start<=t&&+a.dataset.end>t)?.focus({preventScroll:!0})}_place(e,t){let s=this.getBoundingClientRect(),a=e.getBoundingClientRect(),i=300;if(t)return{x:x(a.left-s.left,0,s.width-i),y:a.bottom-s.top+6};let n=a.right-s.left+8;return{x:n+i>s.width?x(a.left-s.left-i-8,0,s.width-i):n,y:a.top-s.top}}_openSlot(e,t,s){let[a,i]=this.rules.slots[t][s];this.pop={type:"slot",day:t,idx:s,start:m(a),end:m(i),targets:new Set,...this._place(e,!1)}}_openQuota(e,t){this.pop={type:"quota",day:t,value:this.rules.quota[t],days:new Set([t]),...this._place(e.currentTarget,!0)}}_openCopy(e,t){this.pop={type:"copy",day:t,targets:new Set,...this._place(e.currentTarget,!0)}}_close(){this.pop=null}_popError(e){this.pop={...this.pop,error:e}}_applySlot(){let e=this.pop,t=me(e.start),s=me(e.end);if(t==null||s==null)return this._popError("slot_missing");if(s===0&&(s=f),s<=t)return this._popError("slot_order");if(s-t<ge)return this._popError("slot_too_short");let a=[...e.targets].filter(i=>i!==e.day);return this._focusAfter={day:e.day,start:t},this._edit(i=>{i.slots[e.day].splice(e.idx,1);let n=B(i,e.day,[t,s]);if(n?.error)return n;let l=!!n;for(let d of a){if(n=B(i,d,[t,s]),n?.error)return n;l||=!!n}return a.length?{info:"duplicated",params:{n:a.length,merged:l}}:l?{info:"merged"}:null}),this._close()}_deleteSlot(){let{day:e,idx:t}=this.pop;this._edit(s=>{s.slots[e].splice(t,1)},"slot_deleted"),this._close()}_applyQuota(){let{value:e,days:t}=this.pop;this._edit(s=>{for(let a of t)s.quota[a]=e},t.size>1?"quota_applied":null,{value:e?b(e):"0",n:t.size}),this._close()}_applyCopy(){let{day:e,targets:t}=this.pop;t.size&&(this._edit(s=>{for(let a of t)s.slots[a]=I(s.slots[e]),s.quota[a]=s.quota[e]},"day_copied",{day:e,n:t.size}),this._close())}_dayChips(e,t){let s=this.t,a=()=>this.pop={...this.pop},i=d=>{e.has(d)?e.delete(d):e.add(d),a()},n=d=>{d.forEach(c=>c!==t&&e.add(c)),a()},l=()=>{e.clear(),t==null&&e.add(this.pop.day),a()};return o`
      <div class="chips">
        ${s.days.map(([d],c)=>c===t?p:o`
          <button class="chip ${e.has(c)?"on":""}" aria-pressed=${e.has(c)} @click=${()=>i(c)}>${d}</button>`)}
      </div>
      <div class="shortcuts">
        <button class="link" @click=${()=>n(Ke)}>${s("grid.add_weekdays")}</button>
        <button class="link" @click=${()=>n(We)}>${s("grid.add_weekend")}</button>
        <button class="link" @click=${()=>n(S)}>${s("grid.add_all")}</button>
        ${e.size?o`<button class="link muted" @click=${l}>${s("grid.clear")}</button>`:p}
      </div>`}_renderPop(){let e=this.t,t=this.pop,s;if(t.type==="slot")s=o`
        <h3>${e("grid.slot_title",{day:t.day})}</h3>
        <div class="times">
          <label for="p-start">${e("grid.start")}
            <input id="p-start" type="time" step="300" .value=${t.start} @input=${i=>t.start=i.target.value}>
          </label>
          <span class="arrow" aria-hidden="true">→</span>
          <label for="p-end">${e("grid.end")}
            <input id="p-end" type="time" step="300" .value=${t.end} @input=${i=>t.end=i.target.value}>
          </label>
        </div>
        <p class="note">${e("grid.slot_note")}</p>
        <div class="field-label">${e("grid.duplicate_on")}</div>
        ${this._dayChips(t.targets,t.day)}
        ${t.error?o`<p class="error" role="alert">${e(`error.${t.error}`)}</p>`:p}
        <div class="actions">
          <button class="text danger" @click=${this._deleteSlot}>${e("grid.delete")}</button>
          <span class="grow"></span>
          <button class="text" @click=${this._close}>${e("grid.cancel")}</button>
          <button class="filled" @click=${this._applySlot}>${e("grid.apply")}</button>
        </div>`;else if(t.type==="quota"){let i=n=>this.pop={...t,value:x(n,0,f)};s=o`
        <h3>${e("grid.quota_title",{day:t.day})}</h3>
        <div class="stepper">
          <button class="round" aria-label=${e("grid.minus15")} @click=${()=>i(t.value-15)}>−</button>
          <output>${t.value?b(t.value):e("grid.no_tv")}</output>
          <button class="round" aria-label=${e("grid.plus15")} @click=${()=>i(t.value+15)}>+</button>
        </div>
        <div class="presets">
          ${[0,30,60,90,120,180].map(n=>o`
            <button class="chip ${t.value===n?"on":""}" @click=${()=>i(n)}>${n?b(n):e("grid.preset_none")}</button>`)}
        </div>
        <div class="field-label">${e("grid.apply_to")}</div>
        ${this._dayChips(t.days,null)}
        <div class="actions">
          <span class="grow"></span>
          <button class="text" @click=${this._close}>${e("grid.cancel")}</button>
          <button class="filled" ?disabled=${!t.days.size} @click=${this._applyQuota}>${e("grid.apply")}</button>
        </div>`}else{let i=this.rules.slots[t.day],n=this.rules.quota[t.day];s=o`
        <h3>${e("grid.copy_title",{day:t.day})}</h3>
        <p class="note">${e("grid.copy_note",{quota:n?b(n):e("grid.none_m"),slots:i.length?i.map(([l,d])=>`${m(l)}\u2013${m(d)}`).join(", "):e("grid.none_f")})}</p>
        <div class="field-label">${e("grid.to")}</div>
        ${this._dayChips(t.targets,t.day)}
        <div class="actions">
          <span class="grow"></span>
          <button class="text" @click=${this._close}>${e("grid.cancel")}</button>
          <button class="filled" ?disabled=${!t.targets.size} @click=${this._applyCopy}>${e("grid.copy")}</button>
        </div>`}let a={slot:"grid.dlg_slot",quota:"grid.dlg_quota",copy:"grid.dlg_copy"}[t.type];return o`
      <div class="backdrop" @pointerdown=${this._close}></div>
      <div class="pop" role="dialog" aria-label=${e(a)} style="left:${t.x}px; top:${t.y}px"
           @keydown=${i=>i.key==="Escape"&&this._close()}>
        ${s}
      </div>`}_slot(e,t,[s,a],i,n){if(a<=i)return p;let l=this.drag,d=l?.moved&&l.idx===t&&l.day===e,c=Math.max(s,i),h=(a-c)*n;return o`
      <div class="slot ${d?"ghost":""} ${h<30?"compact":""}" style="top:${(c-i)*n}px; height:${h}px"
           data-day=${e} data-idx=${t} data-start=${s} data-end=${a} tabindex="0" role="button"
           aria-label=${this.t("grid.slot_aria",{day:e,start:m(s),end:m(a)})}
           @keydown=${_=>this._slotKey(_,e,t)}>
        <span class="handle" data-handle="start"></span>
        <span class="label">
          ${h<30?`${m(s)}\u2013${m(a)}`:o`${m(s)}<br>${m(a)}`}
          ${h>=58?o`<small>${b(a-s)}</small>`:p}
        </span>
        <span class="handle end" data-handle="end"></span>
      </div>`}render(){if(!this.rules||!this.t)return p;let e=this.t,t=this.rules,s=this._px,a=this._top,i=Be(),n=[];for(let h=a;h<=f;h+=60)n.push(h);let l=new Date,d=l.getHours()*60+l.getMinutes(),c=this.drag?.moved?this.drag.preview:null;return o`
      <div class="toolbar">
        <p class="hint">
          <span class="mouse">${e("grid.hint_mouse")}</span>
          <span class="touch">${e("grid.hint_touch")}</span>
        </p>
        <div class="toggles">
          <label for="fine"><input id="fine" type="checkbox" .checked=${this.fine} @change=${h=>this.fine=h.target.checked}> ${e("grid.fine")}</label>
          <label for="night"><input id="night" type="checkbox" .checked=${this.showNight} @change=${h=>this.showNight=h.target.checked}> ${e("grid.night")}</label>
        </div>
      </div>

      <div class="head">
        <div class="corner"></div>
        ${e.days.map(([h],_)=>{let u=t.quota[_],g=W(t.slots[_]),v=!u||!t.slots[_].length,z=!v&&u>g,R=g?Math.min(100,u/g*100):0;return o`
            <div class="day ${_===i?"today":""}">
              <button class="dayname" @click=${ee=>this._openCopy(ee,_)} aria-label=${e("grid.copy_day_aria",{day:_})}>
                ${h}<span class="dots" aria-hidden="true">⋯</span>
              </button>
              <button class="quota ${v?"off":""} ${z?"warn":""}" @click=${ee=>this._openQuota(ee,_)}
                      aria-label=${e("grid.quota_aria",{day:_,value:u?b(u):e("grid.none_m")})}>
                ${u?b(u):"\u2014"}
              </button>
              <div class="gauge ${z?"warn":""}"
                   title=${g?e("grid.gauge_title",{quota:u?b(u):"0",total:b(g)}):e("grid.gauge_none")}>
                <span style="width:${R}%"></span>
              </div>
            </div>`})}
      </div>

      <div class="body" style="height:${(f-a)*s}px">
        <div class="axis" aria-hidden="true">
          ${n.map(h=>o`<span style="top:${(h-a)*s}px">${h===f?"24:00":m(h)}</span>`)}
        </div>
        <div class="cols" style="--hour:${60*s}px"
             @pointerdown=${this._down} @pointermove=${this._move} @pointerup=${this._up} @pointercancel=${this._cancel}>
          ${S.map(h=>o`
            <div class="col ${h===i?"today":""} ${!t.quota[h]||!t.slots[h].length?"off":""}">
              ${t.slots[h].map((_,u)=>this._slot(h,u,_,a,s))}
              ${c&&c.day===h?o`
                <div class="slot preview" style="top:${(Math.max(c.start,a)-a)*s}px; height:${(c.end-Math.max(c.start,a))*s}px">
                  <span class="label">${m(c.start)}<br>${m(c.end)}</span>
                </div>`:p}
              ${h===i&&d>=a?o`<div class="now" style="top:${(d-a)*s}px" title=${e("grid.now")}></div>`:p}
            </div>`)}
        </div>
      </div>
      ${this.pop?this._renderPop():p}`}static styles=$`
    :host { display: block; position: relative; --slot: var(--child, var(--zp-primary)); }
    button { font: inherit; color: inherit; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 8px 20px; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .hint { margin: 0; color: var(--zp-muted); max-width: 62ch; line-height: 1.45; }
    .hint .touch { display: none; }
    @media (hover: none) {
      .hint .touch { display: inline; }
      .hint .mouse { display: none; }
    }
    .toggles { display: flex; gap: 16px; color: var(--zp-muted); }
    .toggles label { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; white-space: nowrap; }
    .toggles input { accent-color: var(--zp-primary); margin: 0; }

    .head, .body { display: grid; grid-template-columns: 2.9rem 1fr; }
    .head {
      grid-template-columns: 2.9rem repeat(7, minmax(0, 1fr)); position: sticky; top: 0; z-index: 3;
      background: var(--zp-card); padding-block: 6px 10px;
    }
    .day { display: grid; justify-items: center; gap: 4px; padding-inline: 2px; min-width: 0; }
    .dayname {
      border: 0; background: none; padding: 4px 6px; border-radius: 8px; font-weight: 600; cursor: pointer;
      display: inline-flex; gap: 2px; align-items: baseline;
    }
    .dayname .dots { color: var(--zp-muted); font-size: 12px; opacity: 0; transition: opacity .15s; }
    .dayname:hover .dots, .dayname:focus-visible .dots { opacity: 1; }
    .day.today .dayname { color: var(--zp-primary); }
    .quota {
      border: 1px solid var(--zp-line); background: var(--zp-card); border-radius: 999px; padding: 3px 8px; cursor: pointer;
      font-variant-numeric: tabular-nums; font-size: 12.5px; font-weight: 600; white-space: nowrap; max-width: 100%;
      overflow: hidden; text-overflow: ellipsis;
    }
    .quota:hover { border-color: var(--slot); }
    .quota.off { color: var(--zp-muted); font-weight: 500; }
    .quota.warn { border-color: var(--zp-warn); background: var(--zp-warn-bg); }
    .gauge { width: 70%; height: 3px; border-radius: 3px; background: var(--zp-line-soft); overflow: hidden; }
    .gauge span { display: block; height: 100%; background: var(--slot); border-radius: inherit; }
    .gauge.warn span { background: var(--zp-warn); }

    .body { position: relative; margin-top: 6px; }
    .axis { position: relative; }
    .axis span {
      position: absolute; right: 8px; transform: translateY(-50%); font-size: 11px; color: var(--zp-muted);
      font-variant-numeric: tabular-nums;
    }
    .cols {
      position: relative; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));
      border-top: 1px solid var(--zp-line); border-left: 1px solid var(--zp-line); cursor: crosshair;
      user-select: none; -webkit-user-select: none;
      background-image: linear-gradient(var(--zp-line) 1px, transparent 1px), linear-gradient(var(--zp-line-soft) 1px, transparent 1px);
      background-size: 100% var(--hour), 100% calc(var(--hour) / 2);
    }
    .col { position: relative; border-right: 1px solid var(--zp-line); touch-action: pan-y; }
    .col.off { background: repeating-linear-gradient(135deg, transparent 0 7px, var(--zp-line-soft) 7px 8px); }
    .col.today { background-color: color-mix(in srgb, var(--zp-primary) 5%, transparent); }
    .now { position: absolute; left: -1px; right: 0; height: 2px; background: var(--zp-danger); pointer-events: none; z-index: 2; }
    .now::before {
      content: ""; position: absolute; left: -4px; top: -3px; width: 8px; height: 8px; border-radius: 50%; background: var(--zp-danger);
    }

    .slot {
      position: absolute; left: 3px; right: 3px; box-sizing: border-box; border-radius: 7px; overflow: hidden;
      background: color-mix(in srgb, var(--slot) 22%, var(--zp-card));
      border: 1px solid color-mix(in srgb, var(--slot) 70%, var(--zp-card));
      color: var(--zp-ink); cursor: grab; touch-action: none; z-index: 1; transition: box-shadow .12s;
      display: flex; align-items: flex-start;
    }
    .slot:hover { box-shadow: 0 2px 8px rgb(0 0 0 / .12); }
    .slot:focus-visible { outline: 2px solid var(--slot); outline-offset: 2px; z-index: 2; }
    .slot:active { cursor: grabbing; }
    .slot.ghost { opacity: .3; }
    .slot.preview {
      border-style: dashed; background: color-mix(in srgb, var(--slot) 32%, var(--zp-card)); z-index: 4;
      pointer-events: none; box-shadow: var(--zp-shadow);
    }
    .label {
      padding: 4px 6px; font-size: 11.5px; line-height: 1.25; font-weight: 600; font-variant-numeric: tabular-nums;
      pointer-events: none; overflow: hidden;
    }
    .label small { display: block; font-weight: 500; color: var(--zp-muted); margin-top: 2px; }
    .slot.compact .label { padding-block: 0; white-space: nowrap; font-size: 10.5px; }
    .handle { position: absolute; left: 0; right: 0; top: 0; height: 8px; cursor: ns-resize; }
    .handle.end { top: auto; bottom: 0; }
    .handle::after {
      content: ""; position: absolute; left: 50%; width: 18px; height: 3px; margin-left: -9px; top: 2px; border-radius: 2px;
      background: var(--slot); opacity: 0; transition: opacity .12s;
    }
    .handle.end::after { top: auto; bottom: 2px; }
    .slot:hover .handle::after, .slot:focus-visible .handle::after { opacity: .8; }
    @media (max-width: 639px) {
      .label { font-size: 10.5px; padding: 3px 4px; }
      .label small { display: none; }
      .head, .body { grid-template-columns: 2.4rem 1fr; }
      .head { grid-template-columns: 2.4rem repeat(7, minmax(0, 1fr)); }
      .axis span { font-size: 10px; right: 5px; }
      .quota { padding: 2px 5px; font-size: 11px; }
    }

    .backdrop { position: fixed; inset: 0; z-index: 9; }
    .pop {
      position: absolute; z-index: 10; width: 300px; box-sizing: border-box; padding: 16px; border-radius: 14px;
      background: var(--zp-raised); border: 1px solid var(--zp-line); box-shadow: var(--zp-shadow); display: grid; gap: 10px;
    }
    @media (max-width: 639px) {
      .backdrop { background: rgb(0 0 0 / .35); }
      .pop {
        position: fixed; left: 0 !important; right: 0; top: auto !important; bottom: 0; width: auto;
        border-radius: 18px 18px 0 0; padding-bottom: calc(18px + env(safe-area-inset-bottom, 0px));
      }
    }
    h3 { margin: 0; font-size: 15px; }
    .times { display: flex; align-items: end; gap: 8px; }
    .times label { display: grid; gap: 4px; font-size: 12px; color: var(--zp-muted); flex: 1; }
    .times .arrow { padding-bottom: 9px; color: var(--zp-muted); }
    input[type="time"] {
      font: inherit; font-size: 15px; color: var(--zp-ink); background: var(--zp-card); border: 1px solid var(--zp-line);
      border-radius: 8px; padding: 6px 8px; font-variant-numeric: tabular-nums; min-width: 0; color-scheme: inherit;
    }
    input:focus-visible, button:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 2px; }
    .note { margin: 0; color: var(--zp-muted); font-size: 12.5px; line-height: 1.4; }
    .field-label {
      font-size: 12px; font-weight: 600; color: var(--zp-muted); text-transform: uppercase; letter-spacing: .05em; margin-top: 4px;
    }
    .chips, .presets { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
      border: 1px solid var(--zp-line); background: var(--zp-card); border-radius: 999px; padding: 4px 10px; cursor: pointer;
      font-size: 13px; font-variant-numeric: tabular-nums;
    }
    .chip.on { background: var(--slot); border-color: var(--slot); color: #fff; }
    .shortcuts { display: flex; flex-wrap: wrap; gap: 4px 12px; }
    .link { border: 0; background: none; padding: 2px 0; color: var(--zp-primary); cursor: pointer; font-size: 12.5px; }
    .link.muted { color: var(--zp-muted); }
    .stepper { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .stepper output { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .round {
      width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--zp-line); background: var(--zp-card);
      font-size: 20px; cursor: pointer;
    }
    .error { margin: 0; color: var(--zp-danger); font-size: 13px; }
    .actions { display: flex; align-items: center; gap: 6px; margin-top: 6px; }
    .grow { flex: 1; }
    .text, .filled { border-radius: 999px; padding: 7px 14px; cursor: pointer; font-weight: 600; border: 0; }
    .text { background: none; color: var(--zp-primary); }
    .text.danger { color: var(--zp-danger); padding-inline: 6px; }
    .filled { background: var(--zp-primary); color: var(--zp-primary-ink); }
    .filled:disabled { opacity: .45; cursor: default; }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; }
    }
  `};customElements.define("zapette-week-grid",$e);var et="zapette-panel-entry",tt="zapette-panel-view",st=["children","history","settings"],qt=r=>{history.pushState(null,"",r),window.dispatchEvent(new CustomEvent("location-changed",{detail:{replace:!1}}))},we=class extends y{static properties={hass:{attribute:!1},narrow:{type:Boolean},_instances:{state:!0},_entryId:{state:!0},_title:{state:!0},_kids:{state:!0},_current:{state:!0},_toast:{state:!0},_saving:{state:!0},_codeError:{state:!0},_loadError:{state:!0},_view:{state:!0},_settingsDirty:{state:!0}};constructor(){super(),this._instances=null,this._kids=[],this._saved={},this._undo={},this._toast=null,this._saving=!1,this._view="children",this._settingsDirty=!1;try{let e=localStorage.getItem(tt);st.includes(e)&&(this._view=e)}catch{}this._onBeforeUnload=e=>{(this._dirtyKids().length||this._settingsDirty)&&e.preventDefault()}}connectedCallback(){super.connectedCallback(),window.addEventListener("beforeunload",this._onBeforeUnload)}disconnectedCallback(){window.removeEventListener("beforeunload",this._onBeforeUnload),super.disconnectedCallback()}get _t(){let e=this.hass?.locale?.language??this.hass?.language;return this._tLang!==e&&(this._tLang=e,this._tCache=Fe(e)),this._tCache}willUpdate(e){e.has("hass")&&this.hass&&this._instances===null&&!this._loading&&this._loadInstances()}async _loadInstances(){this._loading=!0;try{this._instances=await this.hass.callWS({type:"zapette/instances"});let e=null;try{e=localStorage.getItem(et)}catch{}let t=this._instances.find(s=>s.entry_id===e)??this._instances[0];t&&await this._loadChildren(t.entry_id)}catch(e){this._loadError=e.message??String(e)}finally{this._loading=!1}}async _loadChildren(e){let t=await this.hass.callWS({type:"zapette/children",entry_id:e});this._entryId=e,this._title=t.title,this._kids=t.children.map(s=>({...s,color:N(s.color)})),this._saved=Object.fromEntries(this._kids.map(s=>[s.subentry_id,this._snapshot(s)])),this._undo={},this._kids.some(s=>s.subentry_id===this._current)||(this._current=this._kids[0]?.subentry_id);try{localStorage.setItem(et,e)}catch{}}async _reloadChildren(e){let t=Object.fromEntries(this._dirtyKids().map(a=>[a.subentry_id,a])),s=this._undo;await this._loadChildren(this._entryId),this._kids=this._kids.map(a=>{let i=t[a.subentry_id];return i?{...a,enabled:i.enabled,quota:i.quota,slots:i.slots}:a}),this._undo=Object.fromEntries(Object.entries(s).filter(([a])=>this._kids.some(i=>i.subentry_id===a))),e&&this._kids.some(a=>a.subentry_id===e)&&(this._current=e)}_onChildChanged(e){let{action:t,subentry_id:s}=e.detail;this._reloadChildren(t==="deleted"?null:s)}_onRenamed(e){this._title=e.detail.title,this._instances=this._instances.map(t=>t.entry_id===this._entryId?{...t,title:e.detail.title}:t)}_dialogs(){return this.renderRoot.querySelector("zapette-child-dialogs")}async _switchInstance(e){if((this._dirtyKids().length||this._settingsDirty)&&!confirm(this._t("panel.discard_confirm"))){e.target.value=this._entryId;return}this._dirtyKids().length&&this._discard(),this._settingsView()?.discard(),await this._loadChildren(e.target.value)}_settingsView(){return this.renderRoot.querySelector("zapette-settings")}_setView(e){if(e!==this._view){if(this._view==="settings"&&this._settingsDirty){if(!confirm(this._t("panel.discard_confirm")))return;this._settingsView()?.discard(),this._settingsDirty=!1}this._view=e;try{localStorage.setItem(tt,e)}catch{}}}get _kid(){return this._kids.find(e=>e.subentry_id===this._current)}_snapshot(e){return JSON.stringify({enabled:e.enabled,quota:e.quota,slots:e.slots})}_isDirty(e){return!e.invalid&&this._snapshot(e)!==this._saved[e.subentry_id]}_dirtyKids(){return this._kids.filter(e=>this._isDirty(e))}_update(e,t){let s=this._undo[e.subentry_id]||=[];s.push(this._snapshot(e)),s.length>50&&s.shift(),this._kids=this._kids.map(a=>a===e?{...a,...t}:a)}_showToast(e,t="info"){clearTimeout(this._toastTimer),this._toast={text:e,kind:t},this._toastTimer=setTimeout(()=>this._toast=null,3500)}_errorText(e){let t=this._t,s=t(`error.${e.code}`),a=He.indexOf(e.message);return s===`error.${e.code}`?e.message??String(e):a>=0?`${s} (${t.days[a][1]})`:s}_onEdit(e){let t=this._t,s=this._kid,a=I({quota:s.quota,slots:s.slots}),i=e.detail.mutate(a);if(i?.error){this._showToast(t(`error.${i.error}`,i.params),"error");return}this._update(s,a);let n=i?.info??e.detail.info;n&&this._showToast(t(`info.${n}`,i?.params??e.detail.params))}_undoLast(){let e=this._kid,t=this._undo[e.subentry_id]?.pop();t&&(this._kids=this._kids.map(s=>s===e?{...s,...JSON.parse(t)}:s),this._showToast(this._t("panel.undone")))}_toggleEnabled(e){this._update(this._kid,{enabled:e.target.checked})}_copyFrom(e){let t=this._kids.find(a=>a.subentry_id===e.target.value);if(e.target.value="",!t)return;let s=this._kid;this._update(s,{quota:I(t.quota),slots:I(t.slots)}),this._showToast(this._t("panel.copied_from",{src:t.name,name:s.name}))}async _save(){let e=this._t;this._saving=!0;let t=[];for(let s of this._dirtyKids())try{let a=await this.hass.callWS({type:"zapette/child/update",entry_id:this._entryId,subentry_id:s.subentry_id,enabled:s.enabled,quota:s.quota,slots:s.slots}),i={...s,...a};this._kids=this._kids.map(n=>n.subentry_id===s.subentry_id?i:n),this._saved[s.subentry_id]=this._snapshot(i),this._undo[s.subentry_id]=[],t.push(s.name)}catch(a){this._showToast(e("panel.save_error",{name:s.name,message:this._errorText(a)}),"error"),this._saving=!1;return}this._saving=!1,this._showToast(e("panel.saved",{names:t.join(", ")}),"ok")}_discard(){this._kids=this._kids.map(e=>this._isDirty(e)?{...e,...JSON.parse(this._saved[e.subentry_id])}:e),this._undo={},this._showToast(this._t("panel.discarded"))}_openCode(){this._codeError=null;let e=this.renderRoot.querySelector("#code-dialog");e.querySelector("form").reset(),e.showModal()}async _submitCode(e){e.preventDefault();let t=e.target,s=this._kid;try{await this.hass.callWS({type:"zapette/child/set_code",entry_id:this._entryId,subentry_id:s.subentry_id,code:t.code.value,code_confirm:t.confirm.value})}catch(a){this._codeError=this._errorText(a);return}this.renderRoot.querySelector("#code-dialog").close(),this._showToast(this._t("panel.code_changed",{name:s.name}),"ok")}_renderToolbar(){let e=this._t;return o`
      <div class="toolbar">
        <ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>
        <div class="main-title">Zapette</div>
        ${this._instances?.length>1?o`
          <select class="instance" aria-label=${e("panel.tv")} .value=${this._entryId} @change=${this._switchInstance}>
            ${this._instances.map(t=>o`<option value=${t.entry_id} ?selected=${t.entry_id===this._entryId}>${t.title}</option>`)}
          </select>`:this._title?o`<span class="tv">${this._title}</span>`:p}
      </div>`}_renderEmpty(e,t,s){return o`
      <section class="card empty">
        <h2>${e}</h2>
        <p>${t}</p>
        <button class="filled" @click=${()=>qt(s.path)}>${s.label}</button>
      </section>`}_renderKid(e){let t=this._t;if(e.invalid)return o`<section class="card empty"><p>${t("panel.invalid_child",{name:e.name})}</p></section>`;let s=Qe(e),a=S.reduce((l,d)=>l+Math.min(e.quota[d],W(e.slots[d])),0),i=S.filter(l=>e.quota[l]&&e.slots[l].length).length,n=this._kids.filter(l=>l!==e&&!l.invalid);return o`
      <section class="card childhead">
        <div class="avatar" aria-hidden="true">
          ${e.icon&&customElements.get("ha-icon")?o`<ha-icon .icon=${e.icon}></ha-icon>`:e.name[0]}
        </div>
        <div class="who">
          <h2>${e.name}</h2>
          <p>${i?t("panel.weekly",{total:b(a),n:i}):t("panel.no_day")}</p>
        </div>
        <div class="controls">
          <label class="switch" for="enabled">
            <input id="enabled" type="checkbox" role="switch" .checked=${e.enabled} @change=${this._toggleEnabled}>
            <span class="track"><span class="thumb"></span></span> ${t("panel.enabled")}
          </label>
          <button class="outlined" @click=${this._openCode}>${t("panel.change_code")}</button>
          ${n.length?o`
            <select id="copy-from" class="outlined" @change=${this._copyFrom} aria-label=${t("panel.copy_from")}>
              <option value="">${t("panel.copy_from")}</option>
              ${n.map(l=>o`<option value=${l.subentry_id}>${l.name}</option>`)}
            </select>`:p}
          <button class="outlined icon" @click=${this._undoLast} ?disabled=${!this._undo[e.subentry_id]?.length}
                  title=${t("panel.undo")} aria-label=${t("panel.undo")}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14 4 9l5-5"></path><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"></path></svg>
          </button>
        </div>
      </section>

      <section class="card gridcard">
        <zapette-week-grid .rules=${e} .t=${t} @edit=${this._onEdit}></zapette-week-grid>
      </section>

      <section class="card checks" aria-live="polite">
        <h2>${t("panel.checks")}</h2>
        ${s.length?o`<ul>${s.map(l=>o`<li><span class="tri" aria-hidden="true">!</span>${t(`warn.${l.key}`,l.params)}</li>`)}</ul>`:o`<p class="allgood">${t("panel.all_good",{name:e.name})}</p>`}
      </section>`}_renderContent(){let e=this._t;if(this._loadError)return o`<section class="card empty"><p>${e("panel.load_error",{message:this._loadError})}</p></section>`;if(this._instances===null)return o`<div class="loading" aria-busy="true"></div>`;if(!this._instances.length)return this._renderEmpty(e("panel.no_instance_title"),e("panel.no_instance_text"),{label:e("panel.open_integrations"),path:"/config/integrations/dashboard"});let t=this._kid,s=this._dirtyKids(),a=o`
      <nav class="views" role="tablist" aria-label=${e("panel.views")}>
        ${st.map(i=>o`
          <button role="tab" aria-selected=${this._view===i} @click=${()=>this._setView(i)}>${e(`panel.view_${i}`)}</button>`)}
      </nav>`;return this._view==="settings"?o`
        ${a}
        <div class="intro">
          <h1>${e("settings.title")}</h1>
          <p>${e("settings.intro")}</p>
        </div>
        <zapette-settings .hass=${this.hass} .entryId=${this._entryId} .t=${e}
          @dirty-changed=${i=>this._settingsDirty=i.detail}
          @toast=${i=>this._showToast(i.detail.text,i.detail.kind)}
          @renamed=${this._onRenamed}></zapette-settings>
        ${s.length?this._renderSavebar(s):p}`:this._view==="history"?o`
        ${a}
        <div class="intro">
          <h1>${e("history.title")}</h1>
          <p>${e("history.intro")}</p>
        </div>
        <section class="card gridcard">
          <zapette-history .hass=${this.hass} .entryId=${this._entryId} .t=${e}></zapette-history>
        </section>
        ${s.length?this._renderSavebar(s):p}`:o`
      ${a}
      <div class="intro">
        <h1>${e("panel.title")}</h1>
        <p>${e("panel.intro")}</p>
      </div>

      <nav class="tabs" role="tablist">
        ${this._kids.map(i=>o`
          <button role="tab" class="tab" aria-selected=${i===t} style="--dot:${i.color}" @click=${()=>this._current=i.subentry_id}>
            <span class="dot"></span>${i.name}
            ${this._isDirty(i)?o`<span class="unsaved" title=${e("panel.unsaved")}>●</span>`:p}
          </button>`)}
        <button class="tab add" @click=${()=>this._dialogs().openAdd()}>${e("panel.add_child")}</button>
        ${t?o`
          <span class="manage">
            ${t.invalid?p:o`<button class="link" @click=${()=>this._dialogs().openEdit(t)}>${e("panel.edit_child")}</button>`}
            <button class="link danger" @click=${()=>this._dialogs().openDelete(t)}>${e("panel.delete_child")}</button>
          </span>`:p}
      </nav>

      ${t?o`<div class="kid" style="--child:${t.color}">${this._renderKid(t)}</div>`:o`
        <section class="card empty"><p>${e("panel.no_child",{tv:this._title})}</p></section>`}

      ${s.length?this._renderSavebar(s):p}`}_renderSavebar(e){let t=this._t;return o`
      <div class="savebar" role="region" aria-label=${t("panel.unsaved")}>
        <span>${t("panel.savebar",{names:e.map(s=>s.name).join(", ")})}</span>
        <span class="grow"></span>
        <button class="text" ?disabled=${this._saving} @click=${this._discard}>${t("panel.discard")}</button>
        <button class="filled" ?disabled=${this._saving} @click=${this._save}>${this._saving?t("panel.saving"):t("panel.save")}</button>
      </div>`}render(){if(!this.hass)return p;let e=this._t,t=this._kid;return o`
      ${this._renderToolbar()}
      <div class="content">
        <main>${this._renderContent()}</main>
      </div>
      <zapette-child-dialogs .hass=${this.hass} .entryId=${this._entryId} .t=${e} .kids=${this._kids}
        @child-changed=${this._onChildChanged} @toast=${s=>this._showToast(s.detail.text,s.detail.kind)}></zapette-child-dialogs>
      ${this._toast?o`<div class="toast ${this._toast.kind}" role="status">${this._toast.text}</div>`:p}
      <dialog id="code-dialog" aria-labelledby="code-title">
        <form @submit=${this._submitCode} novalidate>
          <h2 id="code-title">${e("panel.code_title",{name:t?.name??""})}</h2>
          <p class="note">${e("panel.code_note")}</p>
          <label for="code">${e("panel.code")}<input id="code" name="code" type="password" inputmode="numeric" autocomplete="off" required></label>
          <label for="confirm">${e("panel.confirm")}<input id="confirm" name="confirm" type="password" inputmode="numeric" autocomplete="off" required></label>
          ${this._codeError?o`<p class="error" role="alert">${this._codeError}</p>`:p}
          <div class="actions">
            <span class="grow"></span>
            <button type="button" class="text" @click=${()=>this.renderRoot.querySelector("#code-dialog").close()}>${e("grid.cancel")}</button>
            <button type="submit" class="filled">${e("panel.validate")}</button>
          </div>
        </form>
      </dialog>`}static styles=$`
    :host {
      display: block; height: 100%;
      --zp-bg: var(--primary-background-color, #fafafa);
      --zp-card: var(--card-background-color, #fff);
      --zp-raised: var(--card-background-color, #fff);
      --zp-ink: var(--primary-text-color, #212121);
      --zp-muted: var(--secondary-text-color, #727272);
      --zp-line: var(--divider-color, rgb(0 0 0 / .12));
      --zp-line-soft: color-mix(in srgb, var(--zp-line) 45%, transparent);
      --zp-primary: var(--primary-color, #03a9f4);
      --zp-primary-ink: var(--text-primary-color, #fff);
      --zp-warn: var(--warning-color, #ffa600);
      --zp-warn-bg: color-mix(in srgb, var(--zp-warn) 16%, var(--zp-card));
      --zp-danger: var(--error-color, #db4437);
      --zp-ok: var(--success-color, #43a047);
      --zp-shadow: 0 1px 2px rgb(0 0 0 / .08), 0 10px 28px rgb(0 0 0 / .18);
      background: var(--zp-bg); color: var(--zp-ink);
      font-family: var(--ha-font-family-body, var(--mdc-typography-font-family, Roboto, system-ui, sans-serif));
      font-size: 14px;
    }
    button, select, input { font: inherit; color: inherit; }
    .toolbar {
      display: flex; align-items: center; gap: 8px; height: var(--header-height, 56px); box-sizing: border-box; padding: 0 12px;
      background: var(--app-header-background-color, var(--zp-primary)); color: var(--app-header-text-color, #fff);
      border-bottom: var(--app-header-border-bottom, none); font-size: 20px;
    }
    .main-title { margin-inline-start: 12px; font-weight: 400; }
    .tv { font-size: 14px; opacity: .8; padding-inline-start: 12px; border-inline-start: 1px solid currentColor; }
    .instance { font-size: 14px; background: transparent; border: 1px solid currentColor; border-radius: 8px; padding: 4px 8px; color: inherit; }
    .instance option { color: var(--zp-ink); background: var(--zp-card); }
    .content { height: calc(100% - var(--header-height, 56px)); overflow-y: auto; }
    main { max-width: 1080px; margin: 0 auto; padding: 24px 20px 32px; display: grid; gap: 16px; }
    .loading { height: 40vh; }
    .intro h1 { margin: 0 0 4px; font-size: 26px; font-weight: 500; letter-spacing: -.01em; }
    .intro p { margin: 0; color: var(--zp-muted); max-width: 60ch; }

    .views { display: inline-flex; gap: 2px; padding: 3px; border-radius: 999px; background: var(--zp-line-soft); justify-self: start; }
    .views button {
      border: 0; background: none; border-radius: 999px; padding: 6px 16px; cursor: pointer; font-weight: 500; color: var(--zp-muted);
    }
    .views button[aria-selected="true"] { background: var(--zp-card); color: var(--zp-ink); box-shadow: 0 1px 3px rgb(0 0 0 / .15); }
    .tabs { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
    .tab {
      display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--zp-line); background: var(--zp-card);
      border-radius: 999px; padding: 7px 14px; cursor: pointer; font-weight: 500;
    }
    .tab[aria-selected="true"] { border-color: var(--dot); box-shadow: inset 0 0 0 1px var(--dot); }
    .tab .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--dot); }
    .tab .unsaved { color: var(--zp-warn); font-size: 10px; }
    .tab.add { color: var(--zp-primary); border-style: dashed; }
    .link { border: 0; background: none; color: var(--zp-primary); cursor: pointer; padding: 4px; }
    .manage { margin-inline-start: auto; font-size: 13px; display: inline-flex; gap: 4px; }
    .link.danger { color: var(--zp-danger); }

    .kid { display: grid; gap: 16px; }
    .card {
      background: var(--zp-card); border: 1px solid var(--zp-line); border-radius: var(--ha-card-border-radius, 12px);
      padding: 18px; box-shadow: var(--ha-card-box-shadow, none);
    }
    .empty h2 { margin: 0 0 6px; font-size: 18px; }
    .empty p { margin: 0 0 12px; color: var(--zp-muted); }
    .childhead { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 16px; }
    .avatar {
      width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; font-weight: 700; font-size: 19px;
      color: #fff; background: var(--child);
    }
    .who { flex: 1 1 200px; min-width: 0; }
    .who h2 { margin: 0; font-size: 19px; font-weight: 500; }
    .who p { margin: 2px 0 0; color: var(--zp-muted); font-variant-numeric: tabular-nums; }
    .controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
    .outlined { border: 1px solid var(--zp-line); background: var(--zp-card); border-radius: 999px; padding: 7px 14px; cursor: pointer; }
    .outlined.icon { padding: 7px; display: grid; place-items: center; }
    .outlined.icon svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .outlined:disabled { opacity: .4; cursor: default; }
    .switch { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; margin-inline-end: 6px; }
    .switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
    .track { width: 36px; height: 20px; border-radius: 999px; background: var(--zp-line); position: relative; transition: background .15s; }
    .thumb {
      position: absolute; top: 2px; left: 2px; width: 16px; height: 16px; border-radius: 50%; background: #fff;
      box-shadow: 0 1px 2px rgb(0 0 0 / .3); transition: transform .15s;
    }
    .switch input:checked + .track { background: var(--child); }
    .switch input:checked + .track .thumb { transform: translateX(16px); }
    .switch input:focus-visible + .track { outline: 2px solid var(--zp-primary); outline-offset: 2px; }

    .gridcard { padding: 18px 18px 22px; }
    .checks h2 { margin: 0 0 10px; font-size: 15px; font-weight: 500; }
    .checks ul { margin: 0; padding: 0; list-style: none; display: grid; gap: 8px; }
    .checks li { display: flex; gap: 10px; align-items: baseline; line-height: 1.4; }
    .tri {
      flex: none; width: 18px; height: 18px; border-radius: 50%; display: inline-grid; place-items: center; font-size: 12px;
      font-weight: 800; color: var(--zp-ink); background: var(--zp-warn-bg); border: 1px solid var(--zp-warn); transform: translateY(3px);
    }
    .allgood { margin: 0; color: var(--zp-ok); }

    .savebar {
      position: sticky; bottom: 12px; z-index: 5; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px;
      padding: 12px 16px; background: var(--zp-raised); border: 1px solid var(--zp-line); border-radius: 14px; box-shadow: var(--zp-shadow);
    }
    .toast {
      position: fixed; left: 50%; bottom: calc(24px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); z-index: 40;
      background: var(--zp-ink); color: var(--zp-card); padding: 10px 16px; border-radius: 10px; box-shadow: var(--zp-shadow);
      max-width: min(90vw, 480px); text-align: center;
    }
    .toast.error { background: var(--zp-danger); color: #fff; }
    .toast.ok { background: var(--zp-ok); color: #fff; }

    .text, .filled { border-radius: 999px; padding: 8px 16px; cursor: pointer; font-weight: 500; border: 0; }
    .text { background: none; color: var(--zp-primary); }
    .filled { background: var(--zp-primary); color: var(--zp-primary-ink); }
    .text:disabled, .filled:disabled { opacity: .5; cursor: default; }
    button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid var(--zp-primary); outline-offset: 2px; }

    dialog {
      border: 1px solid var(--zp-line); border-radius: 18px; padding: 22px; background: var(--zp-raised); color: var(--zp-ink);
      width: min(92vw, 380px); box-sizing: border-box; box-shadow: var(--zp-shadow);
    }
    dialog::backdrop { background: rgb(0 0 0 / .4); }
    dialog form { display: grid; gap: 12px; }
    dialog h2 { margin: 0; font-size: 18px; font-weight: 500; }
    dialog label { display: grid; gap: 4px; font-size: 12.5px; color: var(--zp-muted); }
    dialog input {
      border: 1px solid var(--zp-line); border-radius: 8px; padding: 9px 10px; background: var(--zp-card); font-size: 16px; letter-spacing: .2em;
    }
    .note { margin: 0; color: var(--zp-muted); font-size: 13px; line-height: 1.4; }
    .error { margin: 0; color: var(--zp-danger); font-size: 13px; }
    .actions { display: flex; gap: 6px; align-items: center; }
    .grow { flex: 1; }

    @media (max-width: 639px) {
      main { padding: 16px 12px 24px; gap: 12px; }
      .intro h1 { font-size: 22px; }
      .card { padding: 14px; }
      .gridcard { padding: 12px 8px 16px; }
      .manage { margin-inline-start: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; }
    }
  `};customElements.define("zapette-panel",we);
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
