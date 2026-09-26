// Test a selectable ZIP using an unpacked Arsenal app in an isolated fixture.
// Usage: node tests/test_arsenal_selectable.cjs <mod.zip> <Arsenal-app-source> <output-dir> [off]
// No live manager profile or game paths are used. Arsenal itself is not distributed.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const crypto = require('crypto');
const source = path.resolve(process.argv[3]);
const base = path.resolve(process.argv[4]);
fs.mkdirSync(base, {recursive: true});
const fixture = path.join(base, 'manager-fixture-' + crypto.randomUUID());
assert(!fs.existsSync(fixture), 'Fixture already exists; inspect before retrying.');
const fsExtra = require(path.join(source, 'node_modules/fs-extra'));
const extractZip = require(path.join(source, 'node_modules/extract-zip'));
const AdmZip = require(path.join(source, 'node_modules/adm-zip'));
const JSON5 = require(path.join(source, 'node_modules/json5'));
const game = path.join(fixture, 'Helldivers 2');
const data = path.join(game, 'data');
const library = path.join(fixture, 'library');
const temp = path.join(fixture, 'temp');
const state = path.join(fixture, 'state');
for (const folder of [data, path.join(game, 'bin'), library, temp, state]) fs.mkdirSync(folder, {recursive:true});
const records = {modsList:[], modsLibrary:[], userModsDir:library, userGameDir:game,
  selectedProfile:'test', dataPath:state, setModsActive:process.argv[5]!=='off', setAllOptionsActive:process.argv[5]!=='off', data:{test:{mods:[]}}};
const logs = [];
const localConsole = Object.fromEntries(['log','warn','error'].map(level=>[level,(...args)=>logs.push({level,message:args.map(String).join(' ')})]));
const utils = {
  readData:(key,all)=>{logs.push({config_read:key,all:!!all});return all?records.data:records[key];},
  writeData:(key,value)=>{records[key]=value;fs.writeFileSync(path.join(state, 'settings.json'),JSON.stringify(records,null,2));},
  cleanFileName:value=>value.replace(/[<>:"/\\|?*]/g,'_'),
  generateUniqueFileName:(name,extension,directory)=>{let result=name,n=1;while(fs.existsSync(path.join(directory,result+extension)))result=name+'-'+n++;return result;},
  stripBOM:value=>value.replace(/^\uFEFF/,''),
  forceDeletePath:async target=>{assert(path.resolve(target).startsWith(fixture+path.sep));await fsExtra.remove(target);},
};
const localDB = {initialized:true, removeModHeaders:()=>true};
const cache = new Map();
function load(relative) {
  const absolute=path.join(source,'obfuscated_src/main',relative);
  if(cache.has(absolute))return cache.get(absolute).exports;
  const module={exports:{}};cache.set(absolute,module);
  function localRequire(name) {
    if(['fs','path','crypto'].includes(name))return require(name);
    if(name==='fs-extra')return fsExtra;
    if(name==='extract-zip')return extractZip;
    if(name==='adm-zip')return AdmZip;
    if(name==='json5')return JSON5;
    if(name==='electron')return {dialog:{showOpenDialog:async()=>{throw new Error('Unexpected UI access');}}};
    if(name.endsWith('/utils')||name==='./utils')return utils;
    if(name.endsWith('/constants'))return {MODS_DIR:library,DATA_PATH:state};
    if(name.endsWith('/LocalDB'))return localDB;
    if(['node-unrar-js','node-7z','7zip-min','7zip-bin'].includes(name))return {};
    if(name.startsWith('.')) {
      const resolved=path.relative(path.join(source,'obfuscated_src/main'),path.resolve(path.dirname(absolute),name+'.js'));
      return load(resolved);
    }
    throw new Error('Unexpected dependency: '+name);
  }
  const context=vm.createContext({module,exports:module.exports,require:localRequire,console:localConsole,
    process:{platform:process.platform,env:{DEV:'true'},resourcesPath:''},Buffer,setTimeout,clearTimeout});
  new vm.Script(fs.readFileSync(absolute,'utf8'),{filename:absolute}).runInContext(context,{timeout:5000});
  return module.exports;
}
const handler=load('modsHandler.js');
const icons=load('modules/iconHandler.js');
const deployer=load('modules/modDeployer.js');
const remover=load('modules/modRemover.js');
const release=path.resolve(process.argv[2]);
const pack=new AdmZip(release);
const manifest=JSON5.parse(pack.readAsText('manifest.json'));
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const listFiles=directory=>fs.readdirSync(directory,{recursive:true,withFileTypes:true}).filter(e=>e.isFile()).map(e=>path.relative(directory,path.join(e.parentPath||e.path,e.name)).replaceAll('\\','/')).sort();
const archive='9ba626afa44a3aa3.patch_0';
const checks=[];
function save(mod){records.modsList=[mod];records.modsLibrary=[mod];records.data.test.mods=[mod];}
function verify(choice){
 assert.equal(listFiles(data).length,choice===null?0:3);
 assert.equal(listFiles(path.join(game,'bin')).length,0);
 if(choice!==null){
  const include=manifest.Options[0].SubOptions[choice].Include[0];
  for(const suffix of ['', '.stream', '.gpu_resources']){
   assert.equal(digest(fs.readFileSync(path.join(data,archive+suffix))),digest(pack.readFile(include+'/'+archive+suffix)));
  }
 }
}
(async()=>{
 await handler.processAndValidateZipsFromRenderer(library,[release]);
 assert.equal(records.modsList.length,1);
 let mod=records.modsList[0];
 assert.equal(mod.uuid,manifest.Guid);assert.equal(mod.label,manifest.Name);
 assert.equal(mod.enabled,records.setModsActive);
 assert.equal(mod.options.length,1);
 // Arsenal auto-enables a sole parent option even when all-options preference is off.
 assert.equal(mod.options[0].enabled,true);
 assert.equal(mod.options[0].include.length,0);
 assert.equal(mod.options[0].suboptions.length,4);
 for(let i=0;i<4;i++){
  const sub=mod.options[0].suboptions[i];
  assert.equal(sub.name,manifest.Options[0].SubOptions[i].Name);
  assert.equal(sub.include[0],manifest.Options[0].SubOptions[i].Include[0]);
  assert.equal(sub.enabled,i===0);
 }
 save(mod);
 // Same purge-and-deploy cycle as manager deployment; every old/new pair is checked.
 async function deploy(choice,parent=true,enabled=true){
  await remover.purgeMods();assert.equal(listFiles(game).length,0);
  mod.enabled=enabled;mod.options[0].enabled=parent;
  mod.options[0].suboptions.forEach((sub,i)=>{sub.enabled=i===choice;});save(mod);
  const result=await deployer.deployMod(mod.uuid,[mod],data,temp,state,[mod]);
  mod=result[0];save(mod);
  verify(enabled&&parent?choice:null);
 }
 for(let old=0;old<4;old++)for(let next=0;next<4;next++){
  await deploy(old);await deploy(next);checks.push({from:old,to:next,payload_matches:true});
 }
 await deploy(null);await deploy(1,false);await deploy(2,true,false);await deploy(0);
 await remover.purgeMods();assert.equal(listFiles(game).length,0);
 const result={manager_version:JSON.parse(fs.readFileSync(path.join(source,'package.json'))).version,
  release_sha256:digest(fs.readFileSync(release)),one_mod:true,one_parent_option:true,
  exclusive_suboptions:4,default_suboption:0,import_enable_preference:records.setAllOptionsActive,
  checks,no_selection_parent_disabled_mod_disabled:true,purge_leaves_fixture_empty:true,
  payload_hashes_preserved:true,live_profile_changed:false,game_launched:false};
 fs.writeFileSync(path.join(base,'arsenal-selectable-'+(records.setAllOptionsActive?'on':'off')+'.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result,null,2));
})().catch(error=>{fs.writeFileSync(path.join(fixture,'backend-log.json'),JSON.stringify(logs,null,2));console.error(error);process.exitCode=1;});
