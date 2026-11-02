if(rows.size()!==2)throw Error('Only rejected default-output override should be removed');
if(restored.length!==85)throw Error('Unexpected native default recipe count');
if(removed.length!==67)throw Error('Unexpected default-output removal count');
