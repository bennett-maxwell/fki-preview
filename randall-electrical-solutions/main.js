
(()=>{const b=document.querySelector('[data-menu]'),n=document.querySelector('[data-nav]');
if(b&&n){b.addEventListener('click',()=>{const o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')});}
const f=document.querySelector('[data-lead-form]');
if(f){f.addEventListener('submit',e=>{e.preventDefault();const hp=f.querySelector('.hp');if(hp&&hp.value)return;const ok=f.querySelector('.ok');if(ok)ok.hidden=false;f.reset();});}
})();
